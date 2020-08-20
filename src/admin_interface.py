from config import Config


# Setup function
def setup_admin_interface(bot):
    # Yells at the member for not being an admin
    async def you_are_not_admin(ctx):
        await ctx.send(f'**You can\'t do that {ctx.author.mention}!**', delete_after=3.0)
        await ctx.message.delete()

    # Sets a channel in DB
    @bot.command(brief='Sets a channel in DB', hidden=True)
    async def set_channel(ctx, name, channel_id):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        try:
            # Get rid of '<#...>'
            id_int = int(channel_id[2:-1])

            # Check if channel exists
            if not bot.get_channel(id_int):
                return await ctx.send(f'Channel {channel_id} does not exist!')

            # Set it as write channel
            Config.set(f'{name}-channel', str(id_int))
            await ctx.send(f'`{name}` channel is now {channel_id}!')
        except ValueError:
            return await ctx.send("Invalid channel name, did you remember to add a '#'?")

    # Purges ideas
    @bot.command(hidden=True)
    async def purge(ctx, name=''):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        if not name:
            return await ctx.send("Please input the name of the channel as in the database.")

        # Get the channel
        chanid = Config.get(f'{name}-channel')
        if not chanid:
            return await ctx.send('Invalid channel, please input the channel name as in the database.')
        chanid = int(chanid)
        chan = bot.get_channel(chanid)
        await ctx.send(f'Purged <#{chanid}>')

        # Purge the channel
        await chan.purge()

    @bot.command(hidden=True)
    async def ahelp(ctx):  # Shows the admin commands

        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        commands = bot.commands
        commands_str = '```'
        for command in commands:  # Get all the commands
            if not command.hidden:  # The command must be hidden
                continue
            commands_str += command.name  # Add the command name
            parameters = command.clean_params

            for parameter in parameters.keys():
                commands_str += f' [{parameter}]'  # Add the parameter name
            commands_str += "\n"  # Add a new line

        commands_str += '```'

        await ctx.send(commands_str)

    @bot.command(hidden=True)
    async def change_voting_period(ctx, days, hours="0", minutes="0", seconds="0"):

        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)
        try:
            time_to_wait = int(days) * 24 * 60 * 60 + int(hours) * 60 * 60 + int(minutes) * 60 + int(seconds)
            Config.set("time-to-wait", str(time_to_wait))
            await ctx.send(ctx.author.mention + ", voting will now last for " + str(time_to_wait) + " seconds.")
        except ValueError:
            await ctx.send(ctx.author.mention + ", please input a valid integer.")

    @bot.command(hidden=True)
    async def change_required_votes(ctx, new_req_votes):

        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)
        try:
            int(new_req_votes)
            Config.set('required-votes', new_req_votes)
            await ctx.send(ctx.author.mention + ", the required votes are now " + new_req_votes)
        except ValueError:
            await ctx.send(ctx.author.mention + ", please input a valid integer")
