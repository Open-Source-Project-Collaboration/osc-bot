# api's
import discord
from discord.ext import commands

# dotenv
from os import path, environ
from dotenv import load_dotenv

# modules
from member_interface import setup_member_interface
from admin_interface import setup_admin_interface

# Database
from config import Config


# Get .env config
dotenv_path = path.join(path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)


# Create bot
prefix = '#!'
bot = commands.Bot(command_prefix=prefix)


# Setup interfaces
setup_member_interface(bot)
setup_admin_interface(bot)


# Set default configs
Config.set_init('idea-channel', '744885478188384287')
Config.set_init('overview-channel', '744885556613480509')


# Startup
@bot.event
async def on_ready():
    print('I\'m alive, my dear human :)')


# Watch for reaction add
@bot.event
async def on_raw_reaction_add(reaction):

    # Get the project role
    idea_id = int(Config.get('idea-channel'))
    chan = bot.get_channel(idea_id)
    message = await chan.fetch_message(reaction.message_id)
    if reaction.channel_id == idea_id and message.author.bot:
        embed = message.embeds[0]
        guild = bot.get_guild(reaction.guild_id)
        member = guild.get_member(reaction.user_id)
        role = discord.utils.get(guild.roles, name=embed.title)

        # Add user to role
        await member.add_roles(role)


# Watch for reaction remove
@bot.event
async def on_raw_reaction_remove(reaction):

    # Get the project role
    chan = bot.get_channel(reaction.channel_id)
    message = await chan.fetch_message(reaction.message_id)
    idea_id = int(Config.get('idea-channel'))
    if reaction.channel_id == idea_id and message.author.bot:
        embed = message.embeds[0]
        guild = bot.get_guild(reaction.guild_id)
        member = guild.get_member(reaction.user_id)
        role = discord.utils.get(guild.roles, name=embed.title)
        # Remove user from role

        if member == message.mentions[0]:  # If the reaction remover is the owner of the idea
            if len(role.members) > 1:  # If there are members in the current role
                new_content = message.content.replace(message.mentions[0].mention, role.members[1].mention)
                await message.edit(content=new_content)
                # Replace the owner with the second member in the role

            else:
                await message.edit(content=message.content.replace(message.mentions[1].mention, "No owner"))

        await member.remove_roles(role)


# Run bot
bot.run(environ.get('DISCORD_TOKEN'))
