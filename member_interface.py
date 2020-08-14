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
        msg = await chan.send(f'{ctx.author.mention} proposed an idea:\n\n> {idea}\n\n In `{lang}`')
        await msg.add_reaction('👍')
