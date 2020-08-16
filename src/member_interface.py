import asyncio

config = {
    'idea-channel': '742718894690795550'
}
TIME_TO_WAIT = 10
ROCKET_EMOJI = '\U0001F680'
CHECK_MARK_EMOJI = '\U0001F973'


# Setup function
def setup_member_interface(bot):
    # Show currently used idea channel
    @bot.command()
    async def idea_channel(ctx):
        chanid = config['idea-channel']
        await ctx.send(f'Current idea channel is <#{chanid}>')

    async def wait_for_idea(message_id, channel, idea):
        await asyncio.sleep(TIME_TO_WAIT)
        voters = ''
        message = await channel.fetch_message(message_id)
        for voter in message.mentions:
            voters += voter.mention + "\n"
        five_check_marks = CHECK_MARK_EMOJI * 5
        await channel.send(five_check_marks + "\n\nVoting for the following idea has ended:\n```" + idea +
                           "```\nParticipants:\n" +
                           voters)

    # Proposes a new idea to idea channel
    @bot.command(brief="Adds a new idea to the ideas channel",
                 description="Adds a new idea to the ideas channel takes the programming language as a first argument, \
                 and the idea explanation as a second argument")
    async def new_idea(ctx, lang='', idea=''):
        chanid = int(config['idea-channel'])
        chan = bot.get_channel(chanid)
        author_mention = ctx.author.mention
        if lang == '':
            return await ctx.send(author_mention + ", please input the language name as the first argument")
        if idea == '':
            return await ctx.send(author_mention + ", please input the explanation for the idea as a second argument")
        msg = await chan.send(
            f'{ROCKET_EMOJI * 5} \n\n {ctx.author.mention} proposed an idea:\
            \n```{idea}```\nProgramming Language: `{lang}`\n**Voters:**\n'
        )
        await msg.add_reaction('👍')
        await wait_for_idea(msg.id, chan, idea)
