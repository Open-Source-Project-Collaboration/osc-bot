import discord.ext.commands
from github import Github

import random

from discord_database.team import Team
from discord_interface.member_interface import github_token, org_name

from reddit_interface.teams_posts_templates import titles, bodies
from reddit_interface.reddit_functions import get_post_input


def setup_reddit_interface(bot: discord.ext.commands.Bot):  # Bot commands related to the reddit implementation go here,
    # it is preferable to add functions to another file
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
        title = await get_post_input(bot, ctx, titles, title_embed, "...")
        # Asks the user to fill out the required information

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
        pass
