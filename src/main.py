# api's
import discord
from discord.ext import commands

# dotenv
from os import path, environ
from dotenv import load_dotenv

# modules
from ideas import setup_ideas


# Get .env config
dotenv_path = path.join(path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


# Create bot
prefix = '#!'
bot = commands.Bot(command_prefix=prefix)


# Setup modules
setup_ideas(bot)


# Startup
@bot.event
async def on_ready():
    print('I\'m alive, my dear human :)')


# Run bot
bot.run(environ.get('DISCORD_TOKEN'))