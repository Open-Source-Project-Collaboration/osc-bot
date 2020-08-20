import asyncio
from config import Config
import discord.ext.commands.errors

CHECK_MARK_EMOJI = '\U0001F973'
RESTART_EMOJI = '\U0001F504'
THUMBS_UP_EMOJI = '\N{THUMBS UP SIGN}'


# Setup function
def setup_member_interface(bot):
    # Show channels
    @bot.command(brief="Shows all the channels that are related to the voting process")
    async def channels(ctx):
        chans = Config.channels()
        msgs = [f'{name} channel is <#{chans[name]}>' for name in chans.keys()]
        msg = '\n'.join(msgs)
        await ctx.send(msg)

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
        gen_name = '-'.join(idea_name.split(' '))
        for item in ['`', '"', '*', '_', '@']:  # Filter out unwanted characters
            lang = lang.replace(item, '')
            idea_explanation = idea_explanation.replace(item, '')
            gen_name = gen_name.replace(item, '')
            idea_name = idea_name.replace(item, '')

        # Check if there is an idea team with the current idea
        role = discord.utils.get(ctx.guild.roles, name=gen_name)
        if role:
            return await ctx.send(ctx.author.mention + ", this idea name already exists.")

        # Check if there is currently a proposed idea with the same title
        messages = await chan.history().flatten()
        for message in messages:
            if message.embeds and message.embeds[0].title == idea_name:
                return await ctx.send(ctx.author.mention + ", this idea name already exists.")

        try:
            # Notify with embed
            embed = discord.Embed(title=idea_name, color=0x00ff00)
            embed.add_field(name="Idea Explanation", value=idea_explanation)
            embed.add_field(name='Programming Language', value=lang, inline=False)
            msg = await chan.send(f'{ctx.author.mention} proposed an idea:', embed=embed)
            await msg.add_reaction('👍')

            # Watch it
            await wait_for_votes(msg.id, idea_name)
        except discord.HTTPException:
            await overview_channel.send(ctx.author.mention +
                                        ", an error has occurred while processing one of your ideas")

    @bot.command(brief="Shows information about the voting process")
    async def voting_info(ctx):
        time_to_wait = Config.get('time-to-wait')
        req_votes = Config.get('required-votes')
        await ctx.send(f'The current voting period is {time_to_wait} seconds.\n' +
                       f'The required votes for each idea are {req_votes} votes.')

    # Asks user for github
    async def get_github(voter, idea_name):  # TODO: Complete function
        await voter.send(f"""
            Hello!
            We noticed that you have voted for {idea_name}
            Please send your GitHub profile so I can add you to the team ^_^
        """)

    # Watches a vote for 14 days
    async def wait_for_votes(message_id, idea_name):

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
            for reaction in msg.reactions:
                if reaction.emoji == THUMBS_UP_EMOJI:
                    users = await reaction.users().flatten()  # Find the users of this reaction
                    voters_number = len(users)
                    for user in users:
                        if user == msg.mentions[0]:  # If the user is the owner of the idea, continue
                            continue
                        participants += "\n" + user.mention

            req_votes = int(Config.get('required-votes'))
            # Check votes (-1 the bot)
            if voters_number > req_votes:
                await msg.delete()
                return await overview_chan.send(
                    f'''
                    {CHECK_MARK_EMOJI * voters_number}\n\n''' +
                    f'''Voting for {idea_name} has ended, **approved**!\n'''
                    f'''Participants:\n{participants}
                    ''')

            # If the votes aren't enough
            await overview_chan.send(
                f'Votes for `{idea_name}` were not enough, waiting for more votes...'
            )
            continue  # Wait 14 days more

        # Trials end here
        await overview_chan.send(
            f'The `{idea_name}` idea has been cancelled due to lack of interest :('
        )

        # Delete the message
        await msg.delete()

    # Startup
    @bot.event
    async def on_ready():
        print('I\'m alive, my dear human :)')
        print("Checking for any unfinished ideas...")

        idea_id = int(Config.get('idea-channel'))
        idea_channel = bot.get_channel(idea_id)
        messages = await idea_channel.history().flatten()
        for message in messages:  # Loop through the messages in the ideas channel
            if message.embeds:  # If the message is an idea message containing Embed, add the restart emoji
                print("Found an unfinished idea!")
                await message.add_reaction(RESTART_EMOJI)

        print("No unfinished ideas since last boot")

    # Watch for reaction add
    @bot.event
    async def on_raw_reaction_add(reaction):
        idea_id = int(Config.get('idea-channel'))
        idea_channel = bot.get_channel(idea_id)
        overview_id = int(Config.get('overview-channel'))
        overview_channel = bot.get_channel(overview_id)

        if reaction.channel_id != idea_id:  # Makes sure the reaction added is in the ideas channel
            return

        message = await idea_channel.fetch_message(reaction.message_id)
        if message.author.bot and message.embeds:  # If the message reacted to is by the bot and contains an embed
            # ie: it is an idea message
            embed = message.embeds[0]

            if reaction.emoji.name == THUMBS_UP_EMOJI:
                return

            elif reaction.emoji.name == RESTART_EMOJI and reaction.member.bot:
                # if it is a restart emoji put by the bot, restart the voting period
                idea_name = embed.title
                await overview_channel.send(f'An error occurred while processing the `{idea_name}` idea\n' +
                                            "The voting period has been restarted but your votes are safe.")
                # We remove the reaction in case the voting period gets restarted again
                await message.remove_reaction(reaction.emoji, reaction.member)
                await wait_for_votes(message.id, idea_name)

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
