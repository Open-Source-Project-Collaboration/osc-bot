import asyncio
from admin_interface import config
import discord.ext.commands.errors

TIME_TO_WAIT = 10
ROCKET_EMOJI = '\U0001F680'
CHECK_MARK_EMOJI = '\U0001F973'
MIN_VOTES = 1


# Setup function
def setup_member_interface(bot):
    # Show currently used idea channel
    @bot.command(brief="Use this to view all the channels that are related to the voting process")
    async def channels(ctx):  # To view all the channels related to the idea voting process
        ideas_id = config['idea-channel']
        suggestions_id = config['suggestions-channel']
        overview_id = config['overview-channel']
        await ctx.send(f'The current channel that is used to vote on ideas is <#{ideas_id}>\n' +
                       f'The current channel that is used to suggest ideas is <#{suggestions_id}>\n' +
                       f'The current channel that is show the voting results is <#{overview_id}>')

    async def get_github(voter, idea):  # TODO: Complete function
        voter.send("Hello,\nYou have voted on the following idea:\n```" + idea +
                   "```\nPlease send me your GitHub profile link so I can add you to the project team.")

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
    @bot.command(brief="Adds a new idea to the ideas channel",
                 description="Adds a new idea to the ideas channel takes the programming language as a first argument, \
                 and the idea explanation as a second argument")
    async def new_idea(ctx, lang='', idea=''):
        chanid = int(config['idea-channel'])
        suggestions_id = int(config['suggestions-channel'])
        chan = bot.get_channel(chanid)
        author_mention = ctx.author.mention
        # Check if the user suggested the idea in the idea suggestions channel
        if ctx.message.channel.id != suggestions_id:
            return await ctx.send(author_mention + ", please suggest your ideas in <#" + str(suggestions_id) + ">!")
        if lang == '':
            return await ctx.send(author_mention + ", please input the language name as the first argument")
        if idea == '':
            return await ctx.send(author_mention + ", please input the explanation for the idea as a second argument")
        msg = await chan.send(
            f'{ROCKET_EMOJI * 5} \n\n {ctx.author.mention} proposed an idea:\
            \n```{idea}```\nProgramming Language: `{lang}`\n**Voters:**\n'
        )
        await msg.add_reaction('👍')
        await wait_for_votes(msg.id, chan, idea)
