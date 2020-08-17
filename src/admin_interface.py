config = {
    'idea-channel': '744885478188384287',
    'overview-channel': '744885556613480509',
    'suggestions-channel': '744885520638804026'
}


# Setup function
def setup_admin_interface(bot):
    # Yells at the member for not being an admin
    async def you_are_not_admin(ctx):
        await ctx.send(f'**You can\'t do that {ctx.author.mention}!**', delete_after=3.0)
        await ctx.message.delete()

    # Sets the current channel that is used for ideas
    @bot.command(brief='Sets the channel that is used for ideas', hidden=True)
    async def set_idea_channel(ctx):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        if ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
        else:
            return await ctx.send("Please enter a valid channel name, did you remember " +
                                  "to add a # before the channel name?")

        chanid = channel.id
        # Set it as write channel
        config['idea-channel'] = str(chanid)
        await ctx.send(f'Idea channel channel is now <#{chanid}>!')

    @bot.command(hidden=True)
    async def set_overview_channel(ctx):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        if ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
        else:
            return await ctx.send("Please enter a valid channel name, did you remember " +
                                  "to add a # before the channel name?")

        chanid = channel.id
        # Set it as write channel
        config['overview-channel'] = str(chanid)
        await ctx.send(f'The idea overview channel is now <#{chanid}>!')

    @bot.command(hidden=True)
    async def set_suggestions_channel(ctx):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        if ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
        else:
            return await ctx.send("Please enter a valid channel name, did you remember " +
                                  "to add a # before the channel name?")

        chanid = channel.id
        # Set it as write channel
        config['suggestions-channel'] = str(chanid)
        await ctx.send(f'The idea suggestions channel is now <#{chanid}>!')

    # Purges ideas
    @bot.command(hidden=True)
    async def purge(ctx):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        # Purge ideas
        await ctx.channel.purge()

    @bot.event
    async def on_raw_reaction_add(reaction):
        channel = bot.get_channel(reaction.channel_id)
        message = await channel.fetch_message(reaction.message_id)
        # Check stuff
        if str(channel.id) != config['idea-channel']:
            return
        voter = reaction.member  # The member who performed the reaction
        if reaction.emoji.name != '👍' and not voter.guild_permissions.administrator:
            # The member is not an admin
            await message.remove_reaction(reaction.emoji, reaction.member)
            return await channel.send(
                content=voter.mention + ', you can\'t use that! Please use 👍 only!',
                delete_after=3.0
            )
        if reaction.member not in message.mentions and reaction.emoji.name == '👍' and message.author.bot\
                and not reaction.member.bot:
            await message.edit(content=message.content + "\n" + voter.mention)

    @bot.event
    async def on_raw_reaction_remove(reaction):
        channel = bot.get_channel(reaction.channel_id)
        message = await channel.fetch_message(reaction.message_id)
        # Check stuff
        if str(channel.id) != config['idea-channel']:
            return

        vote_remover_id = reaction.user_id  # Because there is no reaction.member when removing reactions
        vote_remover = await bot.fetch_user(vote_remover_id)
        if vote_remover_id != message.mentions[0].id:  # If the vote remover isn't the user who proposed the idea
            new_content = message.content.replace(vote_remover.mention, '')
            # Removes the member.mention who removed their reaction from the voters
            await message.edit(content=new_content)
