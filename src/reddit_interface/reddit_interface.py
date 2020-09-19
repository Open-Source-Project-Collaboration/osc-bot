import discord.ext.commands
from discord_database.team import Team


def setup_reddit_interface(bot: discord.ext.commands.Bot):  # Bot commands related to the reddit implementation go here,
    # it is preferable to add functions to another file
    @bot.command(brief="Lets the bot make a reddit post about the team")
    async def reddit_post(ctx: discord.ext.commands.Context):
        category: discord.CategoryChannel = ctx.channel.category  # Gets the category in which the command was used
        if not category:  # If the command was used in a channel that does not belong to a category
            return await ctx.send("Please use this command in a team channel")
        team: Team = Team.get(category_id=category.id)  # Gets the team according to the category id
        if not team:  # If not team was found for this category
            return await ctx.send("Please use this command in a team channel")
