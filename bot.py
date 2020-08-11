import discord
from discord.ext import commands

perfix = ">"
bot = commands.Bot(command_prefix='Bot')


@bot.listen()
async def on_message(message):
    if message.content.lower()[0:2] == "#!" :
        who = str(message.author)
        if "-" in message.content.lower():
            project = message.content.split("-")
            emoji = '\N{THUMBS UP SIGN}'
            a = await message.channel.send('> Added project please voted\n_Project Name:_\n**' + project[0][2:len(project[0])] + "**\n_Description:_\n**" + project[1] + "**\n\nBy **" + who[0:len(who)-5] + "**")
            await message.delete() 
            await a.add_reaction(emoji)
        else:
            await message.channel.send("@"+who+" Please add description (-this is description)")
        
bot.run('Token')
