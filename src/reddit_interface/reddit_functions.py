import asyncio
import random

import discord.ext.commands
import praw
import prawcore.exceptions

from reddit_database.languages import Language
from reddit_interface.reddit_configuration import client_secret, client_id, username, password, USER_AGENT


# Waits for the user to send a message starting with r:
async def wait_for_reddit_message(bot, ctx):
    def check(m: discord.Message):
        return m.author == ctx.author and m.channel == ctx.channel and 'r:' in m.content.lower()

    try:
        message = await bot.wait_for('message', check=check, timeout=300)
        return message
    except asyncio.TimeoutError:
        await ctx.send(ctx.author.mention + ", your reddit post has been cancelled for not responding.")
        return None


# When the user decides to create their own post instead of using a ready template
async def get_new_template(bot, ctx):
    await ctx.send("To create your own template, use `r: [template content]` without the '[', ']'")

    def check(m: discord.Message):
        return m.author == ctx.author and m.channel == ctx.channel and 'r:' in m.content.lower()

    message = await bot.wait_for('message', check=check, timeout=300)
    return message.content[2:].lstrip()


# Get the required data in the post, whether the title or the body
async def get_post_input(bot: discord.ext.commands.Bot, ctx, templates_list, embed: discord.Embed, *formatting):
    await ctx.send(ctx.author.mention + ", please replace the ... with the appropriate information.\n"
                                        "Use `r: [information]` without the '[', ']'\n"
                                        "Type `r: another` to generate another template\n"

                                        "Type `r: create` to create your own template", embed=embed)

    message = await wait_for_reddit_message(bot, ctx)
    if not message:
        return
    response = message.content[2:].lstrip()

    if response.lower() == "another":
        if len(templates_list) < 2:
            await ctx.send("Other templates are not available at the moment.")
            return await get_post_input(bot, ctx, templates_list, embed, *formatting)
        while True:
            new = random.choice(templates_list).format(*formatting)
            if new != embed.description:
                break
        embed = discord.Embed(title=embed.title, description=new)
        return await get_post_input(bot, ctx, templates_list, embed, *formatting)

    elif response.lower() == "create":
        return await get_new_template(bot, ctx)

    else:
        return embed.description.replace("...", response)


# Shows a preview of how the post will look like to the user
async def show_post_preview(bot: discord.ext.commands.Bot, ctx: discord.ext.commands.Context, title, body,
                            subreddit=None):
    await ctx.send("Please type `r: [language name]`, where [language name] is "
                   "the programming language that is used in the project")

    programming_language_message = await wait_for_reddit_message(bot, ctx)
    if not programming_language_message:
        return

    programming_language = programming_language_message.content[2:].strip().lower()

    # Tries to find a subreddit in the database that corresponds to the programming language
    language_subreddits = Language.get_all_subreddits(programming_language) or Language.get_all_subreddits('general')
    while True:
        language_subreddit = 'testosc' if not language_subreddits else random.choice(language_subreddits).subreddit
        if language_subreddit != subreddit:
            break
        elif len(language_subreddits) < 2:  # This is reached when the bot fails to post in an initial subreddit
            # and there are no more subreddits to post in
            return await ctx.send("Couldn't find a valid subreddit to post in, please contact an administrator")

    # Checks ability to post in the subreddit
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=USER_AGENT,
                         username=username, password=password)
    try:
        reddit.subreddit(language_subreddit).fullname
    except (prawcore.exceptions.NotFound, prawcore.exceptions.Redirect):
        return await show_post_preview(bot, ctx, title, body, subreddit=language_subreddit)

    # Shows the post preview
    embed = discord.Embed(title=title, description=body)
    content = "Here is how your post will look like on reddit.\n" \
              f"The submission will be made in r/{language_subreddit}\n" \
              "Use `r: confirm` to confirm\n" \
              "Use `r: cancel` to cancel the submission"

    # Allows the user to change the target subreddit if more than one language instance is found
    if len(language_subreddits) > 1:
        content += "\nUse `r: another` to change the subreddit"

    await ctx.send(content, embed=embed)

    response_message = await wait_for_reddit_message(bot, ctx)
    if not response_message:
        return

    response = response_message.content[2:].lstrip().lower()

    if response == "another" and len(language_subreddits) > 1:
        return await show_post_preview(bot, ctx, title, body, subreddit=language_subreddit)
    elif response == "another":  # When the user types r: another while there is only one subreddit available for this
        # language
        await ctx.send("You can't change the subreddit for this case")
        return await show_post_preview(bot, ctx, title, body)
    elif response == "confirm":
        return title, body, language_subreddit, language_subreddits
    elif response == "cancel":
        return
    else:
        await ctx.send("Invalid option.")
        return await show_post_preview(bot, ctx, title, body)
