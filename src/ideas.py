config = {
    "idealist": "742718894690795550"
}


# Import function
def setup_ideas(bot):
    async def no_permission(ctx, message_to_show):  # Shows the user that he has no permission to do something
        await ctx.send(ctx.author.mention + ", " + message_to_show, delete_after=5.0)
        await ctx.message.delete()

    @bot.command(brief='Shows the current channel that is used for ideas')
    async def idealist(ctx, chanid=''):  # Shows the idea channel and changes it if an argument is given by an admin

        # Return current idea-list channel
        if chanid == '':
            chanid = config["idealist"]
            return await ctx.send(
                f'Current `idea-list` channel is <#{chanid}>!'
            )
        if ctx.author.guild_permissions.administrator:

            # get rid of '<#...>'
            chanid = int(chanid[2:-1])

            # Get the channel with id 'chanid'
            chans = filter(
                lambda x: x.id == chanid,
                bot.get_all_channels()
            )
            chans = list(chans)
            chan = chans[0]

            # Set it as write channel
            config["idealist"] = str(chan.id)
            await ctx.send(f'`idea-list` channel is now <#{chan.id}>!')
        else:
            await no_permission(ctx, "you do not have permission to do that.")

    @bot.command(name="new_idea", brief="Adds a new idea to the ideas channel")
    async def add_idea(ctx, idea_name='', idea_description=''):
        author_mention = ctx.author.mention
        if idea_name == '':
            return await ctx.send(author_mention + ", please add a name for your idea")
        if idea_description == '':
            return await ctx.send(author_mention + ", please add a description for your idea")
        idea_channel = bot.get_channel(int(config["idealist"]))
        await idea_channel.send(
            "**A new idea has been added, please vote using a thumbs up if you wish to participate.**"
            + "\n\n **Idea name: **" + idea_name
            + "\n\n **Idea description: **" + idea_description
            + "\n\n **Added by: **" + author_mention
        )

    # Listen ideas emoji reactions
    @bot.event
    async def on_raw_reaction_add(reaction):
        # Sees the reactions added and removes the ones that are not thumbs up in the ideas channel
        channel = bot.get_channel(reaction.channel_id)

        try:
            message = await channel.fetch_message(reaction.message_id)
        except e:
            print("error")
            return

        # Check stuff
        if str(channel) != 'ideas':
            return

        # Remove stuff
        if reaction.emoji.name != '👍' and not reaction.member.guild_permissions.administrator:
            await message.remove_reaction(reaction.emoji, reaction.member)
            await channel.send(
                content='You can\'t use that! Please use 👍 only!',
                delete_after=5.0
            )

    # Purging ideas
    @bot.command(hidden=True)
    async def purge(ctx):  # Used to delete the messages in the ideas channel
        if str(ctx.channel.id) == config['idealist']:
            if ctx.author.guild_permissions.administrator:
                await ctx.channel.purge()
            else:
                await no_permission(ctx, "you do not have permission to do that")
