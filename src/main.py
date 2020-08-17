# api's
import discord
from discord.ext import commands

# dotenv
from os import path, environ
from dotenv import load_dotenv

# modules
from member_interface import setup_member_interface
from admin_interface import setup_admin_interface


# Get .env config
dotenv_path = path.join(path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)


# Create bot
prefix = '#!'
bot = commands.Bot(command_prefix=prefix)


# Setup interfaces
setup_member_interface(bot)
setup_admin_interface(bot)


# Startup
@bot.event
async def on_ready():
    print('I\'m alive, my dear human :)')


# Watch for reaction add
@bot.event
async def on_raw_reaction_add(reaction):

    # Get the project role
    chan = bot.get_channel(reaction.channel_id)
    message = await chan.fetch_message(reaction.message_id)
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
    embed = message.embeds[0]
    guild = bot.get_guild(reaction.guild_id)
    member = guild.get_member(reaction.user_id)
    role = discord.utils.get(guild.roles, name=embed.title)

    # Remove user from role
    await member.remove_roles(role)


# Run bot
bot.run(environ.get('DISCORD_TOKEN'))
