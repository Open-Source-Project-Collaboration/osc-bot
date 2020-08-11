# Import function
def setup_ideas(bot):

    # Listen ideas channel
    @bot.listen()
    async def on_message(message):
        channel = str(message.channel)

        if channel == 'ideas' and message.author != bot.user:
            emoji = '\N{THUMBS UP SIGN}'
            await message.add_reaction(emoji)


    # Listen ideas emoji reactions
    @bot.event
    async def on_raw_reaction_add(reaction):
        channel = bot.get_channel(reaction.channel_id)

        message = None
        try:
            message = await channel.fetch_message(reaction.message_id)
        except e:
            return

        # Check stuff
        if str(channel) != 'ideas':
            return
        elif message.author == bot.user:
            return

        # Remove stuff
        if reaction.emoji.name != '👍':
            await message.remove_reaction(reaction.emoji, reaction.member)
            await channel.send(
                content='You can\'t use that! Please use 👍 only!',
                delete_after=10.0
            )


    # Purging ideas
    @bot.command('purge')
    async def purge(message):
        if str(message.channel) == 'ideas':
            await message.channel.purge()