import asyncio
from config import Config
import discord.ext.commands.errors

TIME_TO_WAIT = 10
CHECK_MARK_EMOJI = '\U0001F973'
REQ_VOTES = 4


# Setup function
def setup_member_interface(bot):


    # Show channels
    @bot.command(brief="Use this to view all the channels that are related to the voting process")
    async def channels(ctx):
        chans = Config.channels()
        msgs = [f'{name} channel is <#{chans[name]}>' for name in chans.keys()]
        msg  = '\n'.join(msgs)
        await ctx.send(msg)


    # Proposes a new idea to idea channel
    @bot.command(brief="Adds a new idea to the ideas channel")
    async def new_idea(ctx, lang, idea):

        # Check fields
        if not lang or not idea:
            return await ctx.send(f'{ctx.author.mention} fields are invalid!')

        # Get channel
        chanid = Config.get('idea-channel')
        chanid = int(chanid)
        chan = bot.get_channel(chanid)
        if chanid == None:
            return await ctx.send('Idea channel is not!')

        # Generate a name from idea
        gen_name = '-'.join(idea.split(' '))

        # Create a role for it
        role = await ctx.guild.create_role(name=gen_name)

        # Add the proposer
        await ctx.author.add_roles(role)

        # Notify with embed
        embed = discord.Embed(title=gen_name, color=0x00ff00)
        embed.add_field(name='Language', value=lang)
        msg = await chan.send(f'{ctx.author.mention}', embed=embed)
        await msg.add_reaction('👍')

        # Watch it
        await wait_for_votes(msg, role)


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
                return await overview_chan.send(f'''
                    {CHECK_MARK_EMOJI * len(role.members)}

                    Voting for {role.mention} has ended, **approved**!
                    Participants: {role.mention}
                ''')

            # If the votes aren't enough
            await overview_chan.send(
                f'Votes for {role.mention} was not enough, waiting for more votes...'
            )
            continue # Wait 14 days more


        # Trials end here
        await overview_chan.send(
            f'The {role.mention} has been cancelled due to lack of interest :('
        )

        # Delete the role with message
        await role.delete()
        await msg.delete()