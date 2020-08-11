import discord
from discord.ext import commands

perfix = "!"
bot = commands.Bot(command_prefix=perfix)

@bot.command()
async def new_idea(ctx,name,description):
    projectlogs = open("projectlogs.txt","r")
    logs = projectlogs.read()
    who = str(ctx.message.author)
    emoji = '\N{THUMBS UP SIGN}'
    if str(ctx.message.channel) != "full-testing":
        await ctx.message.channel.send("{0.author.mention} Please type on #full-testing".format(ctx.message))
    elif logs.find(str(name)) != -1:
        await ctx.message.channel.send("{0.author.mention} There is a project with this name".format(ctx.message))
    elif name == "":
        await ctx.message.channel.send("{0.author.mention} Please add Project Name (!new_idea 'this is Project Name' 'this is description')".format(ctx.message))
    elif description == "":
        await ctx.message.channel.send("{0.author.mention} Please add description (!new_idea 'this is Project Name' 'this is description')".format(ctx.message))
    elif str(ctx.message.channel) == "full-testing" and logs.find(str(name)) == -1:
         projectlogs.close()
         projectlogs = open("projectlogs.txt","a")
         a = await ctx.message.channel.send('> Added project please voted\n_Project Name:_\n**' + name + "**\n_Description:_\n**" + description + "**\n\nBy **" + who[0:len(who)-5] + "**")
         await ctx.message.delete() 
         await a.add_reaction(emoji)
         projectlogs.write(str(a.id) + "|" + name + "|")
    projectlogs.close()

@bot.event
async def on_raw_reaction_add(message):
    projectlogs = open("projectlogs.txt","r")
    logs = projectlogs.read().split("|")
    wichproject = ""
    if  message.emoji.name == '👍' :
        for i in range(len(logs)):  #This for while is search projects by message id
            if logs[i] == str(message.message_id):
                 wichproject = logs[i+1]
                 print(str(message.user_id) + " is voted for " + wichproject)
                 break
    projectlogs.close()

@bot.event
async def on_raw_reaction_remove(message):
    projectlogs = open("projectlogs.txt","r")
    logs = projectlogs.read().split("|")
    wichproject = ""
    if  message.emoji.name == '👍' : 
       for i in range(len(logs)):  #This for while is search projects by message id
            if logs[i] == str(message.message_id):
                wichproject = logs[i+1]
                print(str(message.user_id) + " is removed vote for " + str(wichproject))
                break
    projectlogs.close()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
bot.run('Token')
