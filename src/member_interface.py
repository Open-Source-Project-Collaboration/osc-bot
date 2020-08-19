import asyncio
from config import Config
import discord.ext.commands.errors

TIME_TO_WAIT = 10
CHECK_MARK_EMOJI = '\U0001F973'
REQ_VOTES = 0
RESTART_EMOJI = '\U0001F504'


# Setup function
def setup_member_interface(bot):
    # Show channels
    @bot.command(brief="Use this to view all the channels that are related to the voting process")
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
        for item in ['`', '"', '*', '_']:
            lang = lang.replace(item, '')
            idea_explanation = idea_explanation.replace(item, '')
            gen_name = gen_name.replace(item, '')

        role = discord.utils.get(ctx.guild.roles, name=gen_name)
        if role:
            return await ctx.send(ctx.author.mention + ", this idea name already exists.")

        try:
            # Create a role for it
            role = await ctx.guild.create_role(name=gen_name)

            # Add the proposer
            await ctx.author.add_roles(role)

            # Notify with embed
            embed = discord.Embed(title=gen_name, color=0x00ff00)
            embed.add_field(name="Idea Explanation", value=idea_explanation)
            embed.add_field(name='Programming Language', value=lang, inline=False)
            msg = await chan.send(f'{ctx.author.mention} proposed an idea:', embed=embed)
            await msg.add_reaction('👍')

            # Watch it
            await wait_for_votes(msg, role)
        except discord.HTTPException:
            await overview_channel.send(ctx.author.mention +
                                        ", an error has occurred while processing one of your ideas")

    # Asks user for github
    async def get_github(voter, role):  # TODO: Complete function
        await voter.send(f"""
            Hello!
            We noticed that you have voted for {role.mention}
            Please send your GitHub profile so I can add you to the team ^_^
        """)

    # Watches a vote for 14 days
    async def wait_for_votes(msg, role):

        # Get channels
        overview_chan = Config.get('overview-channel')
        overview_chan = int(overview_chan)
        overview_chan = bot.get_channel(overview_chan)

        # Trial count
        for _ in range(4):

            # Wait for 14 days
            await asyncio.sleep(TIME_TO_WAIT)

            # Check votes (-1 the bot)
            if len(role.members) > REQ_VOTES:
                await msg.delete()
                participants = ''
                for member in role.members:
                    participants += member.mention + '\n'
                return await overview_chan.send(
                    f'''
                    {CHECK_MARK_EMOJI * len(role.members)}\n\n''' +
                    f'''Voting for {role.mention} has ended, **approved**!\n'''
                    f'''Participants:\n{participants}
                    ''')

            # If the votes aren't enough
            await overview_chan.send(
                f'Votes for `{role.name}` were not enough, waiting for more votes...'
            )
            continue  # Wait 14 days more

        # Trials end here
        await overview_chan.send(
            f'The `{role.name}` has been cancelled due to lack of interest :('
        )

        # Delete the role with message
        await role.delete()
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
            guild = bot.get_guild(reaction.guild_id)

            if reaction.emoji.name == '\N{THUMBS UP SIGN}':  # If it is a thumbs up emoji, add the idea role
                member = guild.get_member(reaction.user_id)
                role = discord.utils.get(guild.roles, name=embed.title)

                # Add user to role
                await member.add_roles(role)

            elif reaction.emoji.name == RESTART_EMOJI and reaction.member.bot:
                # if it is a restart emoji put by the bot, restart the voting period
                idea_name = embed.title
                await overview_channel.send(f'An error occurred while processing the `{idea_name}` idea\n' +
                                            "The voting period has been restarted but your votes are safe.")
                role = discord.utils.get(message.guild.roles, name=idea_name)
                # We remove the reaction in case the voting period gets restarted again
                await message.remove_reaction(reaction.emoji, reaction.member)
                if role:
                    await wait_for_votes(message, role)
                else:  # The role was deleted
                    role = await message.guild.create_role(name=idea_name)
                    await wait_for_votes(message, role)

            else:  # If it is another emoji, remove the reaction
                await message.remove_reaction(reaction.emoji, reaction.member)

    # Watch for reaction remove
    @bot.event
    async def on_raw_reaction_remove(reaction):
        # Get the project role
        chan = bot.get_channel(reaction.channel_id)
        message = await chan.fetch_message(reaction.message_id)
        idea_id = int(Config.get('idea-channel'))
        if reaction.channel_id == idea_id and message.author.bot and reaction.emoji.name == '\N{THUMBS UP SIGN}':
            embed = message.embeds[0]
            guild = bot.get_guild(reaction.guild_id)
            member = guild.get_member(reaction.user_id)
            role = discord.utils.get(guild.roles, name=embed.title)
            # Remove user from role

            if member == message.mentions[0]:  # If the reaction remover is the owner of the idea
                if len(role.members) > 1:  # If there are members in the current role
                    new_content = message.content.replace(message.mentions[0].mention, role.members[1].mention)
                    await message.edit(content=new_content)
                    # Replace the owner with the second member in the role

                else:
                    await message.edit(content=message.content.replace(message.mentions[1].mention, "No owner"))

            await member.remove_roles(role)
