import re
import discord

from config import Config
from user import User

from github import Github


async def get_gen_name(idea_name):
    if len(idea_name) > 95:
        return None
    gen_name = '-'.join(idea_name.split(' ')).lower()
    gen_name = re.sub("([^a-z-])+", '', gen_name)  # Remove anything that is not a letter
    gen_name = re.sub("(-)+", '-', gen_name)  # Replace multiple dashes with a single one
    gen_name = gen_name[:-1] if gen_name[-1] == "-" else gen_name
    return gen_name


async def check_team_existence(ctx, team_name, roles):
    author_mention = ctx.author.mention
    role = discord.utils.get(roles, name=team_name)
    category = discord.utils.get(ctx.guild.categories, name=team_name)

    if not category or not role:
        await ctx.send(author_mention + ", invalid team name")
        return None

    if role.permissions.administrator:
        await ctx.send(author_mention + ", you can't do that")
        return None

    return role


async def delete_from_running(bot, gen_name):
    running_channel_id = int(Config.get('running-channel'))
    running_channel = bot.get_channel(running_channel_id)
    messages = await running_channel.history().flatten()
    for message in messages:
        if not message.embeds or not message.author.bot or message.embeds[0].title != gen_name:
            continue
        await message.delete()


async def delete_entire_team(bot, ctx, team_name, github_token, org_name):
    role = discord.utils.get(ctx.guild.roles, name=team_name)
    if not role:
        return await ctx.send(ctx.author.mention + ", invalid team name")
    leader_role = discord.utils.get(ctx.guild.roles, name='pl-' + team_name)

    category = discord.utils.get(ctx.guild.categories, name=team_name)
    if not category:
        return await ctx.send(ctx.author.mention + ", invalid team name")

    if role.permissions.administrator:
        return await ctx.send(ctx.author.mention + ", you can't do that")

    g = Github(github_token)
    org = g.get_organization(org_name)
    team = org.get_team_by_slug(team_name)
    if not team:
        return await ctx.send("Couldn't find the team on GitHub")

    team.delete()
    for channel in category.channels:
        await channel.delete()
    await category.delete()
    await role.delete()
    if leader_role:
        await leader_role.delete()
    User.delete_team(team_name)
    await delete_from_running(bot, team_name)
