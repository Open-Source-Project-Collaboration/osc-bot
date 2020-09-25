import discord.ext.commands

import asyncio
import random


async def get_new_template(bot, ctx):
    await ctx.send("To create your own template, use `r: [template content]` without the '[', ']'")

    def check(m: discord.Message):
        return m.author == ctx.author and m.channel == ctx.channel and 'r:' in m.content.lower()

    message = await bot.wait_for('message', check=check, timeout=300)
    return message.content[2:].lstrip()


async def get_post_input(bot: discord.ext.commands.Bot, ctx, templates_list, embed: discord.Embed, *formatting):
    await ctx.send(ctx.author.mention + ", please replace the ... with the appropriate information.\n"
                                        "Use `r: [information]` without the '[', ']'\n"
                                        "Type `r: another` to generate another template\n"

                                        "Type `r: create` to create your own template", embed=embed)

    def check(m: discord.Message):
        return m.author == ctx.author and m.channel == ctx.channel and 'r:' in m.content.lower()
    try:
        message = await bot.wait_for('message', check=check, timeout=300)

        if "another" in message.content.lower():
            if len(templates_list) < 2:
                await ctx.send("Other templates are not available at the moment.")
                await get_post_input(bot, ctx, templates_list, embed, *formatting)
            while True:
                new = random.choice(templates_list).format(*formatting)
                if new != embed.description:
                    break
            embed = discord.Embed(title=embed.title, description=new)
            await get_post_input(bot, ctx, templates_list, embed, *formatting)

        elif "create" in message.content.lower():
            return await get_new_template(bot, ctx)

        else:
            information = message.content[2:].lstrip()
            return information

    except asyncio.TimeoutError:
        await ctx.send("Your reddit post has been cancelled for not responding")
        return None


async def show_post_preview(bot: discord.ext.commands.Bot, ctx: discord.ext.commands.Context, title, body):
    message = await ctx.send("Here is how your post will look like on reddit.\n"
                             "Use `r: confirm`")
    pass
