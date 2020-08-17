import asyncio
from admin_interface import config
import discord.ext.commands.errors

TIME_TO_WAIT = 10
ROCKET_EMOJI = '\U0001F680'
CHECK_MARK_EMOJI = '\U0001F973'
MIN_VOTES = 1


# Setup function
def setup_member_interface(bot):


    # Show channels
    @bot.command(brief="Use this to view all the channels that are related to the voting process")
    async def channels(ctx):
        msgs = [f'{key} channel is <#{config[key]}>' for key in config.keys()]
        msg  = '\n'.join(msgs)
        await ctx.send(msg)


    # Asks user for github
    async def get_github(voter, idea):  # TODO: Complete function
        await voter.send(f"""
            Hello!
            We noticed that you have voted for {idea}
            Please send me your GitHub profile link so I can add you to the project team
        """)


    # Watches a vote for 14 days
    async def wait_for_votes(message_id, channel, idea):
        voters = ''  # A string that will contain the voters names each one below the other
        five_check_marks = CHECK_MARK_EMOJI * 5  # Emojis
        message = await channel.fetch_message(message_id)  # The idea message (sent by the bot)
        overview_id = int(config['overview-channel'])  # The idea overview channel
        suggestions_id = int(config['suggestions-channel'])
        suggestions_channel = await bot.fetch_channel(suggestions_id)  # The channel at which the user suggested an idea
        try:
            overview_channel = await bot.fetch_channel(overview_id)  # The channel at which the results are shown

            i = 0  # a variable to check for the number of trials to get enough votes for an idea
            while i < 4:

                await asyncio.sleep(TIME_TO_WAIT)
                message = await channel.fetch_message(message_id)  # Gets the ideas message containing the votes

                if len(message.mentions) >= MIN_VOTES:  # If there are enough votes
                    for voter in message.mentions:  # For each voter, add them to the voters string in a list form
                        voters += voter.mention + "\n"  # TODO: ask each voter for GitHub account link
                    await overview_channel.send(
                        five_check_marks + "\n\nVoting for the following idea has ended:\n```" + idea +
                        "```\nParticipants:\n" +
                        voters
                    )  # Sends the voting results to the overview channel
                    return await message.delete()

                else:  # If the votes aren't enough
                    await overview_channel.send(
                        "Voting for the following idea was not enough, waiting for more votes: \n```"
                        + idea + "```"
                    )  # Wait for more votes and repeat the cycle (3 times)

                i += 1

            # This is reached when the cycle is repeated three times and there aren't enough votes
            await overview_channel.send(
                "The following idea has been cancelled due to lack of interest: \n```" + idea + "```")
            await message.delete()  # Deletes the idea

        except discord.NotFound:  # If the overview channel is not found
            await suggestions_channel.send(
                message.mentions[0].mention +
                ", there has been an error processing your idea, please contact an administrator"
            )
            return await message.delete()


    # Proposes a new idea to idea channel
    @bot.command(brief="Adds a new idea to the ideas channel")
    async def new_idea(ctx, lang, idea):

        # Check fields
        if not lang or not idea:
            return await ctx.send(f'{ctx.author.mention} fields are invalid!')

        # Get channel
        chanid = int(config['idea-channel'])
        chan = bot.get_channel(chanid)
        if chan == None:
            return await ctx.send('Channel does not exists')

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
        await wait_for_votes(msg.id, chan, idea)