config = {
    'idea-channel': '742718894690795550'
}


# Setup function
def setup_member_interface(bot):


    # Show currently used idea channel
    @bot.command()
    async def idea_channel(ctx):
        chanid = config['idea-channel']
        await ctx.send(f'Current idea channel is <#{chanid}>')


    # Proposes a new idea to idea channel
    @bot.command()
    async def new_idea(ctx, lang, idea):
        chanid = int(config['idea-channel'])
        chan = bot.get_channel(chanid)

        msg = await chan.send(f'{ctx.author.mention} proposed:\n> `{idea}` in `{lang}`')
        await msg.add_reaction('👍')