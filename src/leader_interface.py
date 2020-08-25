from config import Config
import discord
from asyncio import TimeoutError


def setup_leader_interface(bot):
    # Tells the user that he is not a leader
    async def you_are_not_leader(ctx):
        await ctx.send(ctx.author.mention + ", you must be in a channel of a team in which you are " +
                       "a leader in order to user this command", delete_after=6.0)
        await ctx.message.delete()

    @bot.command(hidden=True, brief="Leader command")
    async def mark_as_finished(ctx):
        channel = ctx.channel
        category = channel.category
        gen_name = category.name
        leader_role = discord.utils.get(ctx.author.roles, name='pl-' + gen_name)
        # Checks if the user has the leader role
        if not leader_role:
            return await you_are_not_leader(ctx)

        def check(m):  # The predicate that checks the confirm message
            return m.channel == channel and m.author == ctx.author and m.content.lower() == 'yes'

        try:
            await ctx.send("Are you sure you want to mark this project as finished?\n" +
                           "The project channels will be deleted. Reply with a `yes` if you are sure")
            await bot.wait_for('message', check=check, timeout=10.0)
        except TimeoutError:  # If the user did not reply with a yes after 10 seconds
            await ctx.send("Will not mark that as finished")
        else:  # If the user replied with a yes
            for channel in category.channels:  # Delete all the channels related to the team
                await channel.delete()
            finished_channel_id = int(Config.get("finished-channel"))  # The channel to post the finished project
            finished_channel = bot.get_channel(finished_channel_id)
            role = discord.utils.get(ctx.guild.roles, name=gen_name)  # The team role
            participants_str = ''  # A string to hold all the members in the team
            for participant in role.members:  # Check all the role members to add them to the participants string
                participants_str += participant.mention + "\n"
            await finished_channel.send(f'`{gen_name}`\nParticipants:\n{participants_str}')
            # TODO: Add the GitHub repo link
            await role.delete()
            await leader_role.delete()

    @bot.command(hidden=True, brief="Leader command")
    async def lhelp(ctx):
        is_leader = False

        for role in ctx.author.roles:
            if role.name.startswith("pl-"):
                is_leader = True

        if not is_leader and not ctx.author.guild_permissions.administrator:
            return await you_are_not_leader(ctx)

        embed = discord.Embed(title="Leader commands")
        commands = ""

        for command in bot.commands:
            if not command.brief:
                continue
            if "Leader command" in command.brief:  # Every leader command has this in its brief
                commands += command.name + "\n"

        embed.add_field(name="Command", value=commands)
        return await ctx.send(embed=embed)
