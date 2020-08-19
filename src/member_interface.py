import asyncio
from config import Config
import discord.ext.commands.errors

TIME_TO_WAIT = 10
CHECK_MARK_EMOJI = '\U0001F973'
REQ_VOTES = 0


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
    async def new_idea(ctx, lang='', idea_name=''):

        # Check fields
        if not lang or not idea_name:
            return await ctx.send(f'{ctx.author.mention} fields are invalid! ' +
                                  'Please use "language" "idea name" "idea explanations" as arguments')

        # Get channel
        chanid = Config.get('idea-channel')
        chanid = int(chanid)
        chan = bot.get_channel(chanid)
        if not chanid:
            return await ctx.send('Idea channel is not available!')

        # Generate a name from idea
        gen_name = '-'.join(idea_name.split(' '))
        try:
            # Create a role for it
            role = await ctx.guild.create_role(name=gen_name)

            # Add the proposer
            await ctx.author.add_roles(role)

            # Notify with embed
            embed = discord.Embed(title=gen_name, color=0x00ff00)
            embed.add_field(name='Programming Language', value=lang, inline=False)
            msg = await chan.send(f'{ctx.author.mention} proposed an idea:', embed=embed)
            await msg.add_reaction('👍')

            # Watch it
            await wait_for_votes(msg, role)
        except discord.HTTPException:
            await ctx.send(ctx.author.mention + ", the idea name must be less than 100 characters long")

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
        overview_id = int(Config.get('overview-channel'))
        overview_channel = bot.get_channel(overview_id)
        messages = await idea_channel.history().flatten()
        for message in messages:  # Loop through the messages in the ideas channel
            if message.embeds:  # If the message is an idea message containing Embed
                print("Found an unfinished idea")
                idea_name = message.embeds[0].title  # The idea name is the title of the Embed
                # Notify users
                await overview_channel.send(f'There has been a problem processing `{idea_name}`\n' +
                                            "The voting period was restarted but your votes are safe.")

                for role in message.guild.roles:  # Loop through each role
                    if role.name == idea_name:  # If there is a role for the idea
                        return await wait_for_votes(message, role)

                role = await message.guild.create_role(name=idea_name)  # This is reached when the role has been deleted
                await wait_for_votes(message, role)

        print("No unfinished ideas since last boot")
