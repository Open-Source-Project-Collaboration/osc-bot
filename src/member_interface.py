import asyncio
from config import Config
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

# Some constants related to program logic
# TODO: Add them in DB with commands to change them
GITHUB_SLEEP_TIME = 60
GITHUB_REQ_PERCENTAGE = 80 / 100

# GitHub data
github_token = environ.get('GITHUB_TOKEN')
org_name = environ.get('ORG_NAME')

# Bot data
online_since_date = None
utc = pytz.UTC


# TODO: let the bot ask the remaining members for their GitHubs if it was down during the GitHub collection process


# Setup function
def setup_member_interface(bot):
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
        await ctx.send(f'The current voting period is {time_to_wait} seconds.\n' +
                       f'The required votes for each idea are {req_votes} votes.')

    # -------------------------------- Supporting functions --------------------------------
    async def continue_githubs(gen_name, participants_message):
        users = participants_message.mentions
        participants_list = []
        for user in users:
            if not discord.utils.get(user.roles, name=gen_name):
                participants_list.append(user)
        await get_all_githubs(participants_list, gen_name, participants_message)

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

    async def add_github(guild, guild_user, github_user, gen_name):
        github_channel_id = int(Config.get('github-channel'))
        github_channel = guild.get_channel(github_channel_id)
        g = Github(github_token)  # Logs into GitHub
        try:
            g.get_user(github_user)  # Tries to find the user on GitHub
            role = discord.utils.get(guild.roles, name=gen_name)  # Finds the role created in get_all_githubs function
            # Gets information from the server

            # Puts the information in the server
            await guild_user.add_roles(role)  # Adds the role
            embed = discord.Embed(title=github_user)  # Creates an embed with the GitHub username as title
            embed.add_field(name="Idea team", value=gen_name)  # Idea team name (gen_name) as a field
            await github_channel.send(guild_user.mention, embed=embed)  # Send to the GitHub channel in the server
            return True
        except UnknownObjectException:  # If the user's GitHub was not found
            return False

    async def check_submitted(member, gen_name, github_user, channel):
        github_channel_id = int(Config.get('github-channel'))
        github_channel = bot.get_channel(github_channel_id)
        github_messages = await github_channel.history().flatten()
        valid = True

        for message in github_messages:
            # Github message format containing the user
            if message.mentions[0].mention != member.mention:
                continue
            for field in message.embeds[0].fields:
                if field.name == "Idea team" and field.value == gen_name\
                        and message.embeds[0].title != github_user:  # If the user sent a different name
                    await channel.send("Replacing the username you have sent...")
                    await message.delete()
                    break
                elif field.name == "Idea team" and field.value == gen_name\
                        and message.embeds[0].title == github_user:  # If the user sent the same name
                    await channel.send(f'I already have your GitHub account for the `{gen_name}` team.')
                    valid = False
        return valid

    async def check_user_in_server(guild, member_id):
        guild_user = guild.get_member(member_id)
        return guild_user if guild_user else None

    # -------------------------------- Voting logic --------------------------------
    # Proposes a new idea to idea channel
    @bot.command(brief="Adds a new idea to the ideas channel")
    async def new_idea(ctx, lang='', idea_name='', idea_explanation='N/A'):

        # Check fields
        if not lang or not idea_name:
            return await ctx.send(f'{ctx.author.mention} fields are invalid! ' +
                                  'Please use "language" "idea name" "idea explanations" as arguments')

        if len(idea_name) > 100:
            return await ctx.send(ctx.author.mention + ", the idea name length must be less that 100 characters long")

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

        await asyncio.sleep(GITHUB_SLEEP_TIME)

        overview_id = int(Config.get('overview-channel'))
        overview_channel = bot.get_channel(overview_id)
        # If the required percentage or more replied with their GitHub accounts and got their roles added
        if len(role.members) >= GITHUB_REQ_PERCENTAGE * len(message.mentions):
            await overview_channel.send(f'More than {GITHUB_REQ_PERCENTAGE * 100}% ' +
                                        f'of the participants in `{gen_name}` ' +
                                        'replied with their GitHub usernames, idea approved!')
            await message.delete()
            # TODO: Create a category and channels for them
            # TODO: Give the role the permission to access this category
            # TODO: Create GitHub team in the organization
            # TODO: Create GitHub repo in the organization
        else:
            await overview_channel.send(
                f'Less than {GITHUB_REQ_PERCENTAGE * 100}% of the participants in `{gen_name}` '
                + "replied with their GitHub usernames, idea cancelled.")
            await role.delete()
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

        # Check for unfinished processes
        print("Checking for any unfinished ideas...")
        for channel_name in ['idea-channel', 'overview-channel']:
            channel_id = int(Config.get(channel_name))
            channel = bot.get_channel(channel_id)
            channel_messages = await channel.history().flatten()

            for message in channel_messages:  # Loop the messages in the channel
                if message.embeds:  # If the message contains an Embed, add the restart emoji
                    print(f'Found an unfinished process in {channel_name}!')
                    await message.add_reaction(RESTART_EMOJI)

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

            # Checking if the user has already submitted his username
            if not await check_submitted(username_message.author, gen_name, github_user, channel):
                continue

            # Checking if the user is in the server
            guild_user = await check_user_in_server(guild, username_message.author.id)
            if not guild_user:
                return await channel.send("I can't find you in our server.")

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
