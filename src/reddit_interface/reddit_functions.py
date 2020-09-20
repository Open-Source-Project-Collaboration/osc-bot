import discord.ext.commands

import asyncio
import random


async def get_new_template(bot, ctx):
    await ctx.send("To create your own template, use `r: [template content]` without the '[', ']'")

    def check(m: discord.Message):
        return m.author == ctx.author and m.channel == ctx.channel and 'r:' in m.content.lower()

    message = bot.wait_for('message', check=check, timeout=300)
    return message.content[2:].lstrip()


async def get_post_input(bot: discord.ext.commands.Bot, ctx, templates_list, embed: discord.Embed):
    await ctx.send(ctx.author.mention + ", please replace the ... with the appropriate information.\n"
                                        "Use `r: [information]` without the '[', ']'\n"
                                        "Type `r: another` to generate another template\n"

                                        "Type `r: create` to create your own template", embed=embed)

    def check(m: discord.Message):
        return m.author == ctx.author and m.channel == ctx.channel and 'r:' in m.content.lower()
    try:
        message = bot.wait_for('message', check=check, timeout=300)

        if "another" in message.content.lower():
            new = random.choice(templates_list)
            embed = discord.Embed(title=embed.title, description=new)
            await get_post_input(bot, ctx, templates_list, embed)

        elif "create" in message.content.lower():
            new = await get_new_template(bot, ctx)
            embed = discord.Embed(title=embed.title, description=new)
            await get_post_input(bot, ctx, templates_list, embed)

        else:
            information = message.content[2:].lstrip()
            return information

    except asyncio.TimeoutError:
        await ctx.send("Your reddit post has been cancelled for not responding")
        return None

