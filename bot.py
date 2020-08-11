import discord
from discord.ext import commands
from ideas import setup_ideas


# Create bot
prefix = '#!'
bot = commands.Bot(command_prefix=prefix)


# Setup modules
setup_ideas(bot)


# Startup
@bot.event
async def on_ready():
    print('I\'m alive, my dear human :)')


# new-idea command
@bot.command()
async def idea(ctx, name, description):
    await ctx.send('I\'m on it bruh. Stand still...')


# Run bot
token = open('.token').read()
bot.run(token)