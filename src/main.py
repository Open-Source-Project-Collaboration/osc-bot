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


# Set default configs
from config import Config
Config.set_init('idea-channel', '744885478188384287')
Config.set_init('overview-channel', '744885556613480509')
Config.set_init('suggestions-channel', '744885520638804026')


# Startup
@bot.event
async def on_ready():
    print('I\'m alive, my dear human :)')


# Run bot
bot.run(environ.get('DISCORD_TOKEN'))
