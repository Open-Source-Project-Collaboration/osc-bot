from config import Config


# Setup function
def setup_admin_interface(bot):

    # Yells at the member for not being an admin
    async def you_are_not_admin(ctx):
        await ctx.send(f'**You can\'t do that {ctx.author.mention}!**', delete_after=3.0)
        await ctx.message.delete()


    # Sets a channel in DB
    @bot.command(brief='Sets a channel in DB', hidden=True)
    async def set_channel(ctx, name, id):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        # Get rid of '<#...>'
        id_int = int(id[2:-1])

        # Check if channel exists
        if bot.get_channel(id_int) == None:
            return await ctx.send(f'Channel {id} does not exist!')

        # Set it as write channel
        Config.set(f'{name}-channel', str(id_int))
        await ctx.send(f'`{name}` channel is now {id}!')


    # Purges ideas
    @bot.command(hidden=True)
    async def purge(ctx):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        # Get idea channel
        chanid = Config.get('idea-channel')
        chanid = int(chanid)
        chan = bot.get_channel(chanid)
        if chan == None:
            return await ctx.send('Idea channel is not set!')

        # Purge ideas
        await chan.purge()