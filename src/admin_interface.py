config = {
    'idea-channel': '742718894690795550'
}


# Setup function
def setup_admin_interface(bot):
    # Yells at the member for not being an admin
    async def you_are_not_admin(ctx):
        await ctx.send(f'**You can\'t do that {ctx.author.mention}!**', delete_after=3.0)
        await ctx.message.delete()

    # Sets the current channel that is used for ideas
    @bot.command(brief='Sets the channel that is used for ideas', hidden=True)
    async def set_idea_channel(ctx, chanid):

        # Check admin
        if not ctx.author.guild_permissions.administrator:
            return await you_are_not_admin(ctx)

        # Get rid of '<#...>'
        try:
            chanid = int(chanid[2:-1])
            # Set it as write channel
            config['idea-channel'] = str(chanid)
            await ctx.send(f'Idea channel channel is now <#{chanid}>!')
        except ValueError:
            return await ctx.send(f'The specified channel was not found, did you add a # before the channel name?')

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
        if reaction.member not in message.mentions:
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
