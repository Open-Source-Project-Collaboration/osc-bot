import discord
from discord.ext import commands

perfix = ">"
bot = commands.Bot(command_prefix='Bot')

@bot.listen()
async def on_message(message):
    projectlogs = open("projectlogs.txt","r")
    logs = projectlogs.read()
    if message.content.lower()[0:2] == "#!" :
        who = str(message.author)
        if "-" in message.content.lower():
            project = message.content.split("-")
            emoji = '\N{THUMBS UP SIGN}'
            if logs.find(project[0][2:len(project[0])]) > -1:
                await message.channel.send("{0.author.mention} Please type another project name".format(message))
            else:
                projectlogs.close()
                projectlogs = open("projectlogs.txt","a")
                a = await message.channel.send('> Added project please voted\n_Project Name:_\n**' + project[0][2:len(project[0])] + "**\n_Description:_\n**" + project[1] + "**\n\nBy **" + who[0:len(who)-5] + "**")
                await message.delete() 
                await a.add_reaction(emoji)
                projectlogs.write(str(a.id) + "|" + project[0][2:len(project[0])] + "|")
        else:
            await message.channel.send("{0.author.mention} Please add description (-this is description)".format(message))
    projectlogs.close()

    
@bot.event
async def on_raw_reaction_add(message):
    projectlogs = open("projectlogs.txt","r")
    logs = projectlogs.read().split("|")
    #print(message.user_id)
    #print(message.member.name)
    #print(message.emoji.name)
    wichproject = ""
    #print(message)
    if  message.emoji.name == '👍' :
        for i in range(len(logs)):  #This for while is search projects by message id
            #print(str(logs[i]) == str(message.message_id))
            #print(str(logs[i]))
            if logs[i] == message.message_id:
                 wichproject = logs[i+1]
                 print(message.member.name + " is voted for " + wichproject)
                 break
    projectlogs.close()

    
async def on_raw_reaction_remove(message):
    projectlogs = open("projectlogs.txt","r")
    logs = projectlogs.read().split("|")
    wichproject = ""
    #print(message)
    if  message.emoji.name == '👎':
        for i in range(len(logs)):  #This for while is search projects by message id
            #print(str(logs[i]) == str(message.message_id))
            if str(logs[i]) == str(message.message_id):
                wichproject = logs[i+1]
                #print(message.member.name + " is removed vote for " + wichproject)
                break
    projectlogs.close()
bot.run('Token')
