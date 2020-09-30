from discord_database.config import Config
from discord_database.user import User
from discord_database.team import Team
from discord_database.warn import Warn

import discord
from github import Github, UnknownObjectException
import praw
import prawcore.exceptions

from discord_interface.common_functions import delete_entire_team
from discord_interface.member_interface import github_token, org_name

from reddit_database.languages import Language
from reddit_interface.reddit_interface import client_id, client_secret, username, password, USER_AGENT


# Setup function
def setup_admin_interface(bot):
    # Yells at the member for not being an admin
    async def you_are_not_admin(ctx):
        await ctx.send(f'**You can\'t do that {ctx.author.mention}!**', delete_after=3.0)
        await ctx.message.delete()

    # Sets a channel in DB
    @bot.command(brief='Sets a channel in DB', hidden=True)
    async def set_channel(ctx, name, channel_id):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        try:
            # Get rid of '<#...>'
            id_int = int(channel_id[2:-1])

            # Check if channel exists
            if not bot.get_channel(id_int):
                return await ctx.send(f'Channel {channel_id} does not exist!')

            # Set it as write channel
            Config.set(f'{name}-channel', str(id_int))
            await ctx.send(f'`{name}` channel is now {channel_id}!')
        except ValueError:
            return await ctx.send("Invalid channel name, did you remember to add a '#'?")

    # Purges ideas
    @bot.command(hidden=True)
    async def purge(ctx, name=''):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        if not name:
            return await ctx.send("Please input the name of the channel as in the database.")

        # Get the channel
        chanid = Config.get(f'{name}-channel')
        if not chanid:
            return await ctx.send('Invalid channel, please input the channel name as in the database.')
        chanid = int(chanid)
        chan = bot.get_channel(chanid)
        await ctx.send(f'Purged <#{chanid}>')

        # Purge the channel
        await chan.purge()

    @bot.command(hidden=True)
    async def ahelp(ctx):  # Shows the admin commands

        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        commands = bot.commands
        commands_str = '```'
        for command in commands:  # Get all the commands
            if not command.hidden:  # The command must be hidden
                continue
            commands_str += command.name  # Add the command name
            parameters = command.clean_params

            for parameter in parameters.keys():
                commands_str += f' [{parameter}]'  # Add the parameter name
            commands_str += "\n"  # Add a new line

        commands_str += '```'

        await ctx.send(commands_str)

    @bot.command(hidden=True)
    async def change_voting_period(ctx, days, hours="0", minutes="0", seconds="0"):

        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)
        try:
            time_to_wait = int(days) * 24 * 60 * 60 + int(hours) * 60 * 60 + int(minutes) * 60 + int(seconds)
            Config.set("time-to-wait", str(time_to_wait))
            await ctx.send(ctx.author.mention + ", voting will now last for " + str(time_to_wait) + " seconds.")
        except ValueError:
            await ctx.send(ctx.author.mention + ", please input a valid integer.")

    @bot.command(hidden=True)
    async def change_required_votes(ctx, new_req_votes):

        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)
        try:
            int(new_req_votes)
            Config.set('required-votes', new_req_votes)
            await ctx.send(ctx.author.mention + ", the required votes are now " + new_req_votes)
        except ValueError:
            await ctx.send(ctx.author.mention + ", please input a valid integer")

    @bot.command(hidden=True, brief="Deletes from the database the teams which don't have roles")
    async def clean_up_db(ctx):
        roles = ctx.guild.roles
        teams = Team.get_all()
        if not teams:
            return await ctx.send("There are no teams to clean up.")
        deleted_teams = 0
        # Deletes the teams that don't have associated roles
        for team in teams:
            if ctx.guild.get_role(team.role_id) in roles:
                continue
            team.delete_team(team.team_name)
            deleted_teams += 1

        users = User.get_teams()
        deleted_users = 0
        # Deletes the users that aren't in the server
        for user in users:
            if ctx.guild.get_member(user.user_id):
                continue
            User.delete(user.user_id, user.user_team)
            deleted_users += 1

        await ctx.send(f'Database cleaned up. Deleted {deleted_teams} team(s) and {deleted_users} user(s).')

    @bot.command(hidden=True)
    async def change_github_required_percentage(ctx, percentage):
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)
        try:
            percent = str(int(percentage) / 100)
            Config.set('github-required-percentage', percent)
            await ctx.send(ctx.author.mention + ", the required number of voters to reply with their GitHub usernames" +
                           f' in order to approve the idea is now {percentage}%')
        except ValueError:
            await ctx.send(ctx.author.mention + ", please input a valid integer.")

    @bot.command(hidden=True)
    async def change_github_sleep_time(ctx, days, hours="0", minutes="0", seconds="0"):
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)
        try:
            github_sleep_time = int(days) * 24 * 60 * 60 + int(hours) * 60 * 60 + int(minutes) * 60 + int(seconds)
            Config.set("github-sleep-time", str(github_sleep_time))
            await ctx.send(ctx.author.mention + ", voters will now be given " + str(github_sleep_time) + " seconds" +
                           " to reply with their GitHub usernames.")
        except ValueError:
            await ctx.send(ctx.author.mention + ", please input a valid integer.")

    # This command is used in leader voting channels after the users have voted on their project leader to assign the
    # Most voted member as the project leader
    @bot.command(hidden=True)
    async def assign_leader(ctx):
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        voting_channel = ctx.channel
        category = voting_channel.category
        gen_name = category.name  # Gets the team name from the Category name
        team: Team = Team.get(gen_name)

        if not team or voting_channel.id != team.voting_id:
            return await ctx.send(ctx.author.mention + ", this is not a leader voting channel.")

        guild = ctx.guild
        role = ctx.guild.get_role(team.leader_role_id)  # The project leader role created in
        # create_category_channels() function
        if not role:
            role = await guild.create_role(name="pl-" + gen_name)
        if role.members:
            return await ctx.send(ctx.author.mention + ", a project leader already exists for this project")

        messages = await voting_channel.history().flatten()
        leader = None
        max_votes = 0

        for message in messages:
            if not (message.mentions and message.author.bot):
                continue
            thumbs_up_reaction = discord.utils.get(message.reactions, emoji="\N{THUMBS UP SIGN}")
            if not thumbs_up_reaction:
                continue
            voters = await thumbs_up_reaction.users().flatten()
            voters_number = len(voters)
            if voters_number >= max_votes:
                leader_to_add = message.mentions[0]
                team_role = discord.utils.get(leader_to_add.roles, name=gen_name)
                if not team_role:  # Happens when the user has left the team without his name getting removed from the
                    # leader voting
                    continue
                leader = leader_to_add
                max_votes = voters_number

        if not leader:
            return await ctx.send("There is no leader to assign")
        await leader.add_roles(role)
        await voting_channel.delete()
        team.delete_voting_channel(gen_name)
        general_channel = guild.get_channel(team.general_id)
        if not general_channel:
            return
        await general_channel.send(leader.mention + " is now the project leader!")

    @bot.command(hidden=True, brief="Shows the number of warnings a user has received")
    async def warns(ctx, user):
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)
        try:
            member_id = int(user[3:-1])
            warnings = Warn.warnings(member_id)
            return await ctx.send(f'The specified member has {str(warnings)} warning(s).')
        except ValueError:
            return await ctx.send("Please mention a member to show their warnings")

    @bot.command(hidden=True, brief="Deletes a team")
    async def delete_team(ctx, team_name):
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)
        await delete_entire_team(bot, ctx, team_name, github_token, org_name)

    @bot.command(hidden=True, brief="Removes a warning from a member")
    async def unwarn(ctx, user):
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)
        try:
            member_id = int(user[3:-1])
            Warn.unwarn(member_id)
            warnings = Warn.warnings(member_id)
            return await ctx.send(f'The specified member now has {str(warnings)} warning(s).')
        except ValueError:
            return await ctx.send("Please mention a member to show their warnings")

    @bot.command(hidden=True, brief="Sets the users github ids according to their github usernames")  # For migrating db
    async def set_users_ids(ctx):
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        await ctx.send("Please wait...")
        users = User.get_teams()
        g = Github(github_token)
        limit = len(users)
        i = 1
        for user in users:
            await ctx.send(f"Setting the Github id of user ({i}/{limit})")
            try:
                github_user = g.get_user(user.user_github)
                User.set(user.user_id, user.user_team, user.user_github, github_user.id)
                await ctx.send("Success!")
            except UnknownObjectException:
                User.delete(user.user_id, user.user_team)
                await ctx.send("Failed, deleting user.")
            i += 1
        await ctx.send("Done.")

    @bot.command(hidden=True, brief="Adds a new subreddit for a certain language")
    async def add_subreddit(ctx, language, subreddit_name: str):
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)
        await ctx.send("Please wait...")
        subreddit_name = subreddit_name.replace("r/", "")
        if Language.get(language, subreddit_name):
            return await ctx.send("The subreddit already exists for this language.")

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=USER_AGENT,
            username=username,
            password=password
        )
        try:
            reddit.subreddit(subreddit_name).fullname
        except prawcore.exceptions.NotFound and prawcore.exceptions.Redirect:
            return await ctx.send("Could not add this subreddit")

        Language.set(language, subreddit_name)
        await ctx.send("The subreddit has been added successfully")

    @bot.command(hidden=True, brief="Deletes a subreddit for a certain language")
    async def delete_subreddit(ctx, language_name, subreddit_name):
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)
        subreddit_name = subreddit_name.replace("r/", "")

        language = Language.get(language_name, subreddit_name)
        if not language:
            return await ctx.send("The subreddit does not exist for this language.")
        Language.delete(language_name, subreddit_name)
        await ctx.send("Done.")
