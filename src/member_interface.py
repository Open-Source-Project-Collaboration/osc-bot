import asyncio
import contextlib
from discord.ext import tasks
config = {
    'idea-channel': '742718894690795550'
    
}
projectlogs = []



# Setup function
def setup_member_interface(bot,discord):
    # Show currently used idea channel
    @bot.command()
    async def idea_channel(ctx):
        chanid = config['idea-channel']
        await ctx.send(f'Current idea channel is <#{chanid}>')

    # Proposes a new idea to idea channel
    @bot.command(brief="Adds a new idea to the ideas channel",
                     description="Adds a new idea to the ideas channel takes the programming language as a first argument, \
                     and the idea explanation as a second argument")

    @bot.event
    async def on_raw_reaction_add(reaction):
        channel = bot.get_channel(reaction.channel_id)
        message = await channel.fetch_message(reaction.message_id)
        if str(channel.id) != config['idea-channel']:
            return
        else:
            for i in range(len(projectlogs)):
            
                # Check stuff
                if reaction.emoji.name != '👍' and not reaction.member.guild_permissions.administrator:
                    await message.remove_reaction(reaction.emoji, reaction.member)
                    await channel.send(
                        content=reaction.member.mention + ', you can\'t use that! Please use 👍 only!',
                        delete_after=3.0
                    )
                elif message.mentions[0] == reaction.member:
                    warn = ", you can't vote on your own idea, and you can't react to any message you were mentioned in here"
                    await message.remove_reaction(reaction.emoji, reaction.member)
                    await channel.send(
                        content=reaction.member.mention + warn,
                        delete_after=5.0
                    )
                if int(projectlogs[i][1]) == int(reaction.message_id) and int(projectlogs[i][2]) != int(reaction.user_id) and reaction.emoji.name == '👍':
                    projectlogs[i][7] += 1
                    projectlogs[i][8] = 1
        
    @bot.event
    async def on_raw_reaction_remove(reaction):
        channel = bot.get_channel(reaction.channel_id)
        message = await channel.fetch_message(reaction.message_id)
        if str(channel.id) != config['idea-channel']:
            return
        else:
            for i in range(len(projectlogs)):
                if int(projectlogs[i][1]) == int(reaction.message_id) and int(projectlogs[i][2]) != int(reaction.user_id) and reaction.emoji.name == '👍':
                    projectlogs[i][7] -= 1
                    projectlogs[i][8] = 1
                
                
    @bot.command()
    async def new_idea(ctx, lang='',ideaname='', idea=''):
        global projetclogs
        # for block the hacking
        lang = lang.replace('*', '')
        lang = lang.replace('`', '')
        lang = lang.replace('_', '')
        idea = idea.replace('`', '')
        idea = idea.replace('*', '')
        idea = idea.replace('_', '')
        ideaname = ideaname.replace('_', '')
        ideaname = ideaname.replace('`', '')
        ideaname = ideaname.replace('*', '')

        chanid = int(config['idea-channel'])
        chan = bot.get_channel(chanid)
        author_mention = ctx.message.author.mention
        user = bot.get_user(ctx.message.author.id)
        serverid = str(ctx.message.guild.id)
        channelid = str(ctx.message.channel.id)
        
        if lang == '':
            return await ctx.send(author_mention + ", please input the language name as the first argument")
        if idea == '':
            return await ctx.send(author_mention + ", please input the explanation for the idea name as a third argument")
        if ideaname == '':
            return await ctx.send(author_mention + ", please input the explanation for the idea as a second argument")
        if idea != '' and idea != '' and ideaname != '':
            
            embed = discord.Embed(colour=discord.Colour(0x3b8ff0),description="**{2}'s Idea**\n\n_Project Name:_ **{1}**\n_Project Description:_ **{0}**".format(idea,ideaname,author_mention))
            embed.set_author(name="{0.author}".format(ctx.message),icon_url="{0}".format(user.avatar_url))
            embed.set_footer(text="Programming language : {0} , Votes: 0".format(lang))
            embed.set_thumbnail(url="https://minevaganti.org/wp-content/uploads/2020/02/idea.png")
            await ctx.message.delete()
            msg = await chan.send(author_mention,embed=embed)
            await msg.add_reaction('👍')
            projectlogs.append(["https://discordapp.com/channels/" + serverid + "/" + channelid + "/"+ str(msg.id),int(msg.id),int(ctx.message.author.id),user.avatar_url,ideaname,idea,lang,0,0,ctx.message.author.mention,ctx.message.author])
            
    @tasks.loop(seconds=10)
    async def func1():
        with contextlib.suppress(Exception):
            for i in projectlogs:
                if i[8] != 0:
                    chanid = int(config['idea-channel'])
                    chan = bot.get_channel(chanid)
                    channel = bot.get_channel(int(config['idea-channel']))
                    msg = await channel.fetch_message(i[1])
                    embed = discord.Embed(colour=discord.Colour(0x3b8ff0),description="**{2}'s Idea**\n\n_Project Name:_ **{1}**\n_Project Description:_ **{0}**".format(i[5],i[4],i[9]))
                    embed.set_author(name="{0}".format(i[10]),icon_url="{0}".format(i[3]))
                    embed.set_footer(text="Programming language : {0} , Votes: {1}".format(i[6],str(int(i[7])-1)))
                    embed.set_thumbnail(url="https://minevaganti.org/wp-content/uploads/2020/02/idea.png")
                    await msg.edit(embed=embed)
                    i[8] = 0
    func1.start()

