import asyncio
from config import Config
from user import User
import discord.ext.commands.errors
from github import Github, UnknownObjectException
from os import environ
import re
from datetime import datetime, timezone
import pytz

# Used emojis
CHECK_MARK_EMOJI = '\U0001F973'
RESTART_EMOJI = '\U0001F504'
THUMBS_UP_EMOJI = '\N{THUMBS UP SIGN}'

# GitHub data
github_token = environ.get('GITHUB_TOKEN')
org_name = environ.get('ORG_NAME')

# Bot data
online_since_date = None
utc = pytz.UTC


# Setup function
def setup_member_interface(bot):
    # -------------------------------- Extra admin commands --------------------------------
    @bot.command(hidden=True)
    async def start_leader_voting(ctx, team_name):
        guild = ctx.guild
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(ctx.author.mention + ", you can't use this command")

        role = discord.utils.get(guild.roles, name=team_name)
        if not role:
            return await ctx.send("This team doesn't exist")

        leading_role = discord.utils.get(guild.roles, name="pl-" + team_name)
        if leading_role.members:
            return await ctx.send("A leader already exists for this team")

        overwrites = {role: discord.PermissionOverwrite(view_channel=True),
                      guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        category = discord.utils.get(guild.categories, name=team_name)
        if not category:
            return await ctx.send("An error has occurred.")
        await vote_for_leader(role, guild, overwrites, category)
        await ctx.send(f'The leader voting process has been started for `{team_name}`')

    # -------------------------------- Getting info --------------------------------
    # Show channels
    @bot.command(brief="Shows all the channels that are related to the voting process")
    async def channels(ctx):
        chans = Config.channels()
        msgs = [f'{name} is <#{chans[name]}>' for name in chans.keys()]
        msg = '\n'.join(msgs)
        await ctx.send(msg)

    @bot.command(brief="Shows information about the voting process")
    async def voting_info(ctx):
        time_to_wait = Config.get('time-to-wait')
        req_votes = Config.get('required-votes')
        github_sleep_time = Config.get('github-sleep-time')
        github_required_percentage = Config.get('github-required-percentage')
        await ctx.send(f'The current voting period is {time_to_wait} seconds.\n' +
                       f'The required votes for each idea are {req_votes} votes.\n' +
                       f'{float(github_required_percentage) * 100}% of the voters must reply to the bot message ' +
                       "sent to them with their github username to approve the idea.\n" +
                       f'The voters are given {github_sleep_time} seconds to reply with their Github usernames.')

    @bot.command(brief="Shows all teams members and their GitHub usernames")
    async def show_teams(ctx, team_name=''):
        if team_name:  # If the user provided a team name
            users = [User.get_team(team_name)]
            title_name = team_name
        else:  # If the user didn't provide a team name, show all teams
            users = User.get_teams()
            title_name = "Current users in teams"
        users_str = ''
        teams_str = ''
        githubs_str = ''
        embed = discord.Embed(title=title_name)

        if not users:  # Happens when get_teams() function returns None
            return await ctx.send("There are currently no teams.")
        elif users == [None]:  # Happens when get_team() function returns None
            return await ctx.send("There is no team with this name.")

        for user in users:
            guild = ctx.guild
            guild_user = guild.get_member(user.user_id)
            username = guild_user.name
            team = user.user_team
            role = discord.utils.get(guild_user.roles, name=team)
            if not role:  # If the user doesn't have the role (left the team)
                continue
            teams_str += team + "\n"
            github_username = user.user_github
            users_str += username + "\n"
            githubs_str += github_username + "\n"

        users_str = "N/A" if not users_str else users_str
        githubs_str = "N/A" if not githubs_str else githubs_str
        teams_str = "N/A" if not teams_str else teams_str
        embed.add_field(name="Username", value=users_str)
        embed.add_field(name="Team", value=teams_str)
        embed.add_field(name="Github username", value=githubs_str)
        await ctx.send(embed=embed)

    # -------------------------------- Supporting functions --------------------------------
    # Continue asking for Github usernames if the bot goes down
    async def continue_githubs(gen_name, participants_message):
        users = participants_message.mentions
        participants_list = []
        for user in users:
            if not discord.utils.get(user.roles, name=gen_name):  # If the mentioned user doesn't have the role
                participants_list.append(user)
        await get_all_githubs(participants_list, gen_name, participants_message)

    # Checks if an idea team is already created
    async def check_if_finished(gen_name):
        overview_channel_id = int(Config.get('overview-channel'))
        overview_channel = bot.get_channel(overview_channel_id)
        participants_messages = await overview_channel.history().flatten()
        idea_ended = True
        for message in participants_messages:
            if message.embeds and message.embeds[0].title == gen_name:
                # If it is a participants messages containing an Embed
                idea_ended = False
                break

        return idea_ended

    # Adds the team role to the user and his GitHub user name to the db
    async def add_github(guild, guild_user, github_user, gen_name):
        g = Github(github_token)  # Logs into GitHub
        try:
            g.get_user(github_user)  # Tries to find the user on GitHub
            role = discord.utils.get(guild.roles, name=gen_name)  # Finds the role created in get_all_githubs function

            await guild_user.add_roles(role)  # Adds the role
            User.set(guild_user.id, gen_name, github_user)
            return True
        except UnknownObjectException:  # If the user's GitHub was not found
            return False

    # Checks if the user has already submitted the same GitHub username for the same team
    async def check_submitted(member, gen_name, github_user, channel):
        valid = True
        user = User.get(member.id, gen_name)
        role = discord.utils.get(member.roles, name=gen_name)
        if not user:
            return valid
        if user.user_github == github_user:
            await channel.send(f'Your GitHub username `{github_user}` is already set for this team')
            valid = False if role else True  # If the role already exists, there is no need to add it again
        else:
            await channel.send("Replacing your GitHub username...")
        return valid

    async def check_user_in_server(guild, member_id):
        guild_user = guild.get_member(member_id)
        return guild_user if guild_user else None

    # Checks for any unfinished ideas that were stopped when the bot rebooted
    async def check_unfinished_ideas():
        print("Checking for any unfinished ideas...")
        for channel_name in ['idea-channel', 'overview-channel']:
            channel_id = int(Config.get(channel_name))
            channel = bot.get_channel(channel_id)
            channel_messages = await channel.history().flatten()

            for message in channel_messages:  # Loop the messages in the channel
                if message.embeds:  # If the message contains an Embed, add the restart emoji
                    print(f'Found an unfinished process in {channel_name}!')
                    await message.add_reaction(RESTART_EMOJI)

    # -------------------------------- Team creation --------------------------------
    async def vote_for_leader(role, guild, overwrites, category):
        voting_channel = await guild.create_text_channel("leader-voting", overwrites=overwrites, category=category)
        await voting_channel.send("Vote for who you would like to be the project leader")
        for member in role.members:
            if member.bot:
                continue
            voting_message = await voting_channel.send(member.mention)
            await voting_message.add_reaction(THUMBS_UP_EMOJI)

    async def create_category_channels(guild, gen_name):
        role = discord.utils.get(guild.roles, name=gen_name)

        if not role:  # Creates the team role
            role = await guild.create_role(gen_name)

        # Remove the role from the bot
        if role.members:
            for member in role.members:
                if member.bot:
                    await member.remove_roles(role)
                    break

        if not discord.utils.get(guild.roles, name="pl-" + gen_name):  # Creates the leader role
            await guild.create_role(name="pl-" + gen_name, color=discord.Colour(16711680))

        await role.edit(hoist=True)  # Makes the team role show in the members list

        # Only the team role members will be able to view the channel
        overwrites = {role: discord.PermissionOverwrite(view_channel=True),
                      guild.default_role: discord.PermissionOverwrite(view_channel=False)}

        # Tries to see if a category already exists with the team name
        category = discord.utils.get(guild.categories, name=gen_name)
        if not category:  # Creates the team category
            category = await guild.create_category(gen_name, overwrites=overwrites)
        else:
            return
        text_channel = await guild.create_text_channel("General", overwrites=overwrites, category=category)
        await guild.create_voice_channel("Collab room", overwrites=overwrites, category=category)
        await text_channel.send(role.mention + " LET'S GO!!")
        if not role.members:
            return
        await vote_for_leader(role, guild, overwrites, category)

    async def create_team(guild, gen_name):
        await create_category_channels(guild, gen_name)

    # -------------------------------- Voting logic --------------------------------
    # Proposes a new idea to idea channel
    @bot.command(brief="Adds a new idea to the ideas channel")
    async def new_idea(ctx, lang='', idea_name='', idea_explanation='N/A'):

        # Check fields
        if not lang or not idea_name:
            return await ctx.send(f'{ctx.author.mention} fields are invalid! ' +
                                  'Please use "language" "idea name" "idea explanations" as arguments')

        if len(idea_name) > 95:
            return await ctx.send(ctx.author.mention + ", the idea name length must be less that 95 characters long")

        # Get channel
        chanid = Config.get('idea-channel')
        chanid = int(chanid)
        chan = bot.get_channel(chanid)
        overview_id = int(Config.get('overview-channel'))
        overview_channel = bot.get_channel(overview_id)
        if not chanid:
            return await ctx.send('Idea channel is not available!')

        # Generate a name from idea
        gen_name = '-'.join(idea_name.split(' ')).lower()
        for item in ['`', '"', '*', '_', '@', '#']:  # Filter out unwanted characters
            lang = lang.replace(item, '')
            idea_explanation = idea_explanation.replace(item, '')
            gen_name = gen_name.replace(item, '')
        gen_name = re.sub("([^a-z-])+", '', gen_name)  # Remove anything that is not a letter
        gen_name = re.sub("(-)+", '-', gen_name)  # Replace multiple dashes with a single one

        # Check if there is an idea team with the current idea
        role = discord.utils.get(ctx.guild.roles, name=gen_name)
        if role:
            return await ctx.send(ctx.author.mention + ", this idea name already exists.")

        # Check if there is currently a proposed idea with the same title
        messages = await chan.history().flatten()
        for message in messages:
            if message.embeds and message.embeds[0].title == gen_name:
                return await ctx.send(ctx.author.mention + ", this idea name already exists.")

        # Check if the same name exists in the database and if so delete (there would be no current idea with this
        # name anyway, it would be an outdated finished idea)
        User.delete_team(gen_name)

        try:
            # Notify with embed
            embed = discord.Embed(title=gen_name, color=0x00ff00)
            embed.add_field(name="Idea Explanation", value=idea_explanation)
            embed.add_field(name='Programming Language', value=lang, inline=False)
            msg = await chan.send(f'{ctx.author.mention} proposed an idea, please vote using a thumbs up reaction:',
                                  embed=embed)
            await msg.add_reaction('👍')

            # Watch it
            await wait_for_votes(msg.id, gen_name)
        except discord.HTTPException:
            await overview_channel.send(ctx.author.mention +
                                        ", an error has occurred while processing one of your ideas")

    # Asks user for github
    async def get_github(voter, gen_name):
        embed = discord.Embed(title=gen_name)
        embed.add_field(name="Idea", value=gen_name)
        embed.add_field(name="Guild ID", value=voter.guild.id)
        await voter.send('Hello!\nWe noticed that you have voted for the following idea:\n' +
                         'Please send me your GitHub username so I can add you to the team.\n' +
                         "If you receive no reply, then the bot is down or the idea team has already been created.\n" +
                         "If you accidentally send someone else's username, simply re-send your username", embed=embed)

    # Notifies the participants about the idea processing results
    async def notify_voters(participants_message, gen_name):
        overview_id = int(Config.get('overview-channel'))
        message = None
        for member in participants_message.mentions:
            if member.bot:
                continue
            message = await member.send(f'Processing the `{gen_name}` idea has ended. Please check <#{overview_id}>')
        if not message:
            return
        dm_channel = message.channel
        messages = await dm_channel.history().flatten()
        for message in messages:
            if message.embeds and message.author.bot and message.embeds[0].title == gen_name:
                await message.delete()

    async def get_all_githubs(participants, gen_name, message):
        github_sleep_time = int(Config.get('github-sleep-time'))
        github_required_percentage = float(Config.get('github-required-percentage'))
        guild = message.guild
        role = discord.utils.get(guild.roles, name=gen_name)  # Tries to find if a role already exists
        # This happens when the bot is turned off during the GitHub gathering process
        if not role:
            role = await guild.create_role(name=gen_name)  # Creates a role for the team

        for user in participants:
            if not user.bot:
                await get_github(user, gen_name)  # Asks each user for their Github
            else:
                await user.add_roles(role)  # Adds the role to the bot

        await asyncio.sleep(github_sleep_time)

        overview_id = int(Config.get('overview-channel'))
        overview_channel = bot.get_channel(overview_id)
        # If the required percentage or more replied with their GitHub accounts and got their roles added
        if len(role.members) >= github_required_percentage * len(message.mentions):
            await overview_channel.send(f'More than {str(github_required_percentage * 100)}% ' +
                                        f'of the participants in `{gen_name}` ' +
                                        'replied with their GitHub usernames, idea approved!')
            await message.delete()
            await create_team(message.guild, gen_name)
            # TODO: Create a category and channels for them
            # TODO: Give the role the permission to access this category
            # TODO: Create GitHub team in the organization
            # TODO: Create GitHub repo in the organization
        else:
            await overview_channel.send(
                f'Less than {str(github_required_percentage * 100)}% of the participants in `{gen_name}` '
                + "replied with their GitHub usernames, idea cancelled.")
            await role.delete()
            User.delete_team(gen_name)
            await message.delete()

        await notify_voters(message, gen_name)

    # Watches a vote for 14 days
    async def wait_for_votes(message_id, gen_name):

        # Get channels
        overview_chan = Config.get('overview-channel')
        overview_chan = int(overview_chan)
        overview_chan = bot.get_channel(overview_chan)
        idea_id = int(Config.get('idea-channel'))
        idea_channel = bot.get_channel(idea_id)
        msg = None

        # Trial count
        for _ in range(4):
            time_to_wait = int(Config.get('time-to-wait'))
            # Wait for 14 days
            await asyncio.sleep(time_to_wait)
            msg = await idea_channel.fetch_message(message_id)
            voters_number = 0
            participants = msg.mentions[0].mention  # Add the idea owner as an initial participant
            participants_list = [msg.mentions[0]]  # A list to contain Members
            for reaction in msg.reactions:
                if reaction.emoji == THUMBS_UP_EMOJI:
                    users = await reaction.users().flatten()  # Find the users of this reaction
                    voters_number = len(users)
                    for user in users:
                        if user == msg.mentions[0]:  # If the user is the owner of the idea, continue
                            continue
                        participants += "\n" + user.mention
                        participants_list.append(user)

            req_votes = int(Config.get('required-votes'))
            # Check votes (-1 the bot)
            if voters_number > req_votes:
                await msg.delete()
                embed = discord.Embed(title=gen_name)
                participants_message = await overview_chan.send(
                    f'''
                    {CHECK_MARK_EMOJI * voters_number}\n\n''' +
                    f'''Voting for {gen_name} has ended, **approved**!\n'''
                    f'''Participants:\n{participants}\nPlease check your messages
                    ''', embed=embed)
                return await get_all_githubs(participants_list, gen_name, participants_message)

            # If the votes aren't enough
            await overview_chan.send(
                f'Votes for `{gen_name}` were not enough, waiting for more votes...'
            )
            continue  # Wait 14 days more

        # Trials end here
        await overview_chan.send(
            f'The `{gen_name}` idea has been cancelled due to lack of interest :('
        )

        # Delete the message
        await msg.delete()

    # -------------------------------- Bot Events --------------------------------
    # Startup
    @bot.event
    async def on_ready():
        print('I\'m alive, my dear human :)')
        global online_since_date
        online_since_date = datetime.now(tz=timezone.utc)
        await check_unfinished_ideas()
        print("Done.")

    # Watch for reaction add
    @bot.event
    async def on_raw_reaction_add(reaction):
        idea_id = int(Config.get('idea-channel'))
        idea_channel = bot.get_channel(idea_id)
        overview_id = int(Config.get('overview-channel'))
        overview_channel = bot.get_channel(overview_id)

        if reaction.channel_id != idea_id and reaction.channel_id != overview_id:
            # Makes sure the reaction added is in the ideas channel or the overview channel
            return
        if reaction.channel_id == idea_id:
            message = await idea_channel.fetch_message(reaction.message_id)
        else:
            message = await overview_channel.fetch_message(reaction.message_id)
        if message.author.bot and message.embeds:  # If the message reacted to is by the bot and contains an embed
            # ie: it is an idea message
            embed = message.embeds[0]

            if reaction.emoji.name == THUMBS_UP_EMOJI:
                return

            elif reaction.emoji.name == RESTART_EMOJI and reaction.member.bot:
                # if it is a restart emoji put by the bot, restart the voting period
                idea_name = embed.title
                await overview_channel.send(
                    f'Processing the `{idea_name}` idea might take a little longer than expected.')
                # We remove the reaction in case the voting period gets restarted again
                await message.remove_reaction(reaction.emoji, reaction.member)
                if reaction.channel_id == idea_id:
                    await wait_for_votes(message.id, idea_name)
                else:
                    await continue_githubs(idea_name, message)

            else:  # If it is another emoji, remove the reaction
                await message.remove_reaction(reaction.emoji, reaction.member)

    # Watch for reaction remove
    @bot.event
    async def on_reaction_remove(reaction, member):
        message = reaction.message
        idea_id = int(Config.get('idea-channel'))
        if message.channel.id == idea_id and message.author.bot and reaction.emoji == THUMBS_UP_EMOJI:
            if member == message.mentions[0]:  # If the reaction remover is the owner of the idea
                users = await reaction.users().flatten()
                replacer = "No owner "
                if len(users) > 1:  # There are voters other than the bot
                    bot_replace = False
                else:
                    bot_replace = True

                for user in users:  # Replace with bot if there aren't votes, otherwise replace with user
                    if user.bot == bot_replace:
                        replacer = user.mention

                new_content = message.content.replace(message.mentions[0].mention, replacer)
                await message.edit(content=new_content)
                # Replace the owner with the voter

    # Watch messages addition to check for sent GitHub accounts
    @bot.event
    async def on_message(message):
        channel = message.channel
        if channel.type != discord.ChannelType.private:  # If it is not a DM Channel
            return await bot.process_commands(message)  # Process the commands normally

        if message.author.bot:
            return

        messages = await channel.history().flatten()  # Get last 100 messages in DM channel

        # Variables initial declaration
        guild_id = 0
        checked_ideas = 0
        # The username
        username_message = messages[0]  # Gets the last message in DM (the one containing the username)
        github_user = username_message.content

        await channel.send("Hey there, please wait...")
        for message in messages:
            if not message.embeds:
                # Looks for a message containing an embed
                continue
            if utc.localize(message.created_at) < online_since_date and message.author.bot:
                # If it was a message sent before the bot rebooted, delete it
                await message.delete()
                continue

            embed = message.embeds[0]
            gen_name = embed.title  # Gets the idea name from the message sent to user

            for field in embed.fields:
                if field.name == "Guild ID":
                    guild_id = int(field.value)

            guild = bot.get_guild(guild_id)  # Gets the server

            # Checking if team creation process was done
            if await check_if_finished(gen_name):
                continue

            # Checking if the user is in the server
            guild_user = await check_user_in_server(guild, username_message.author.id)

            if not guild_user:
                return await channel.send("I can't find you in our server.")

            # Checking if the user has already submitted his username
            if not await check_submitted(guild_user, gen_name, github_user, channel):
                continue

            # Add the user's GitHub name to the GitHub channel and give the team role
            if await add_github(guild, guild_user, github_user, gen_name):
                await channel.send(f'Thank you! I am currently giving you the `{gen_name}` role...')
                checked_ideas += 1
            else:
                await channel.send("This username is not a valid Github username")
                return
        if checked_ideas > 0:
            return await channel.send("Done")
        else:
            return await channel.send("Nothing to do here :)")
