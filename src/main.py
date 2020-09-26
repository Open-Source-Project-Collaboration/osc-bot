# api's
from discord.ext import commands

# dotenv
from os import path, environ
from dotenv import load_dotenv

# modules
from discord_interface.member_interface import setup_member_interface
from discord_interface.admin_interface import setup_admin_interface
from discord_interface.leader_interface import setup_leader_interface
from reddit_interface.reddit_interface import setup_reddit_interface

# Database
from discord_database.config import Config
from reddit_database.languages import Language

# Get .env config
dotenv_path = path.join(path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

# Create bot
prefix = '#!'
bot = commands.Bot(command_prefix=prefix)

# Setup interfaces
setup_member_interface(bot)
setup_admin_interface(bot)
setup_leader_interface(bot)
setup_reddit_interface(bot)

# Set default configs (channel configs should end with -channel)
Config.set_init('idea-channel', '744885478188384287')
Config.set_init('overview-channel', '744885556613480509')
Config.set_init('bot-channel', '747503630986248313')
Config.set_init('finished-channel', '742442149747884165')
Config.set_init('running-channel', '742692372848312370')
Config.set_init('messages-channel', '755073334995058748')
Config.set_init('reddit-approved-channel', '759436180096942140')
Config.set_init('reddit-pending-channel', '759436129505116222')

Config.set_init('required-votes', '5')
Config.set_init('time-to-wait', '1209600')
Config.set_init('github-sleep-time', '1209600')
Config.set_init('github-required-percentage', '0.7')

Language.set("general", "testosc")

# Run bot
env = environ.get('ENV')
if env == 'dev':
    bot.run(environ.get('DISCORD_DEV_TOKEN'))
else:
    bot.run(environ.get('DISCORD_TOKEN'))
