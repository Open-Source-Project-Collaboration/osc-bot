import discord.ext.commands
from github import Github

import random

from discord_database.team import Team
from discord_interface.member_interface import github_token, org_name

from reddit_interface.teams_posts_templates import titles, bodies, footers
from reddit_interface.reddit_functions import get_post_input, show_post_preview


def setup_reddit_interface(bot: discord.ext.commands.Bot):  # Bot commands and events related
    # to the reddit implementation go here. It is preferable to add functions to another file
    @bot.command(brief="Lets the bot make a reddit post about the team")
    async def reddit_post(ctx: discord.ext.commands.Context):
        category: discord.CategoryChannel = ctx.channel.category  # Gets the category in which the command was used
        if not category:  # If the command was used in a channel that does not belong to a category
            return await ctx.send("Please use this command in a team channel")
        team: Team = Team.get(category_id=category.id)  # Gets the team according to the category id
        if not team:  # If not team was found for this category
            return await ctx.send("Please use this command in a team channel")

        prompt_title = random.choice(titles).format("...")  # Chooses a random title from the title templates
        title_embed: discord.Embed = discord.Embed(title="Post title", description=prompt_title)
        # Asks the user to fill out the required information
        title = await get_post_input(bot, ctx, titles, title_embed, "...")
        if not title:
            return

        # Log into Github to get the repo link
        g = Github(github_token)
        repo = g.get_repo(team.repo_id)
        if not repo:
            return await ctx.send("The team repository was not found, please contact an administrator")
        repo_link = f'https://www.github.com/{org_name}/{repo.name}'

        # Get the channel invite link to be used in the post body
        invite: discord.Invite = await ctx.channel.create_invite()
        invite_link = invite.url

        # Ask the user to fill out the required information
        formatting = ("...", repo_link, invite_link, team.team_name)
        prompt_body = random.choice(bodies).format(*formatting)
        body_embed: discord.Embed = discord.Embed(title="Post body", description=prompt_body)
        body = await get_post_input(bot, ctx, bodies, body_embed, *formatting)
        if not body:
            return

        # Add a footer to the post body
        discord_user = ctx.author.name + "#" + ctx.author.discriminator
        discord_bot = bot.user.name + "#" + bot.user.discriminator
        body += "\n\n" + random.choice(footers).format(discord_user, discord_bot)

        # Shows the preview of the post to be sent to the reddit channel
        post_data = await show_post_preview(bot, ctx, title, body)
        if not post_data:
            return await ctx.send(ctx.author.mention + ", your post has been cancelled.")
        title, body, subreddit = post_data
        print(title, body, subreddit)
        pass
