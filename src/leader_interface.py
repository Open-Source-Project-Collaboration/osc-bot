import discord
from github import Github, UnknownObjectException

from asyncio import TimeoutError

from member_interface import github_token, org_name
from common_functions import delete_entire_team, send_to_finished

from team import Team


def setup_leader_interface(bot):
    # Tells the user that he is not a leader
    async def you_are_not_leader(ctx):
        await ctx.send(ctx.author.mention + ", you must be in a channel of a team in which you are " +
                       "a leader in order to user this command", delete_after=6.0)
        await ctx.message.delete()

    async def check_if_leader(ctx):  # A function that returns the team object if the user is a leader in the category
        # they messaged in or returns None
        channel = ctx.channel
        category: discord.CategoryChannel = channel.category
        team: Team = Team.get(category_id=category.id)
        if not team:
            return team  # None
        leader_role = discord.utils.get(ctx.author.roles, id=team.leader_role_id)
        # Checks if the user has the leader role
        if not leader_role:
            return None
        return team

    @bot.command(hidden=True, brief="Leader command")
    async def mark_as_finished(ctx):
        team = await check_if_leader(ctx)
        if not team:
            return await you_are_not_leader(ctx)

        gen_name = team.team_name

        def check(m):  # The predicate that checks the confirm message
            return m.channel == ctx.channel and m.author == ctx.author and m.content.lower() == 'yes'

        try:
            await ctx.send("Are you sure you want to mark this project as finished?\n" +
                           "The project channels will be deleted. Reply with a `yes` if you are sure")
            await bot.wait_for('message', check=check, timeout=10.0)
        except TimeoutError:  # If the user did not reply with a yes after 10 seconds
            await ctx.send("Will not mark that as finished")
        else:  # If the user replied with a yes
            await delete_entire_team(bot, ctx, gen_name, github_token, org_name)

        await send_to_finished(bot, github_token, org_name, team.repo_id)

    @bot.command(hidden=True, brief="Leader command")
    async def add_repo(ctx, repo_name):
        team = await check_if_leader(ctx)
        if not team:
            return await you_are_not_leader(ctx)
        g = Github(github_token)
        org = g.get_organization(org_name)
        try:
            repo = org.get_repo(repo_name)
            github_team = org.get_team(team.github_id)
            github_team.add_to_repos(repo)
            team.set(
                team.team_name, team.role_id, team.leader_role_id, team.category_id,
                team.general_id, team.github_id, repo.id
            )
            await ctx.send(f"The repository was successfully set to `{repo.name}`")
        except UnknownObjectException:
            return await ctx.send("This repository does not exist in the organization")

    @bot.command(hidden=True, brief="Leader command")
    async def lhelp(ctx):
        if not await check_if_leader(ctx) and not ctx.author.guild_permissions.administrator:
            return await you_are_not_leader(ctx)

        commands = "```"

        for command in bot.commands:
            if not command.brief:
                continue
            if "leader command" not in command.brief.lower():  # Every leader command has this in its brief
                continue
            commands += "\n" + command.name
            for parameter in command.clean_params.keys():
                commands += f' [{parameter}] '

        commands += "\n```"

        return await ctx.send(commands)
