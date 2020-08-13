config = {
    'idea-channel': '742718894690795550'
}


# Setup function
def setup_admin_interface(bot):


    # Yells at the member for not being an admin
    async def you_are_not_admin(ctx):
        await ctx.send(
            f'WHAT ARE YOU DOING YOU F***ING {ctx.author.mention} C*CK'
        )
        await ctx.message.delete()


    # Sets the current channel that is used for ideas
    @bot.command(brief='Sets the current channel that is used for ideas')
    async def set_idea_channel(ctx, chanid):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return you_are_not_admin(ctx)

        # Get rid of '<#...>'
        chanid = int(chanid[2:-1])

        # Check if channel exists
        if bot.get_channel(chanid) == None:
            return await ctx.send(f'`idea-list` channel is now <#{chan.id}>!')

        # Set it as write channel
        config["idealist"] = str(chanid)
        await ctx.send(f'`idea-list` channel is now <#{chanid}>!')


    # Purges ideas
    @bot.command(hidden=True)
    async def purge(ctx):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return you_are_not_admin(ctx)

        # Purge ideas
        await ctx.channel.purge()