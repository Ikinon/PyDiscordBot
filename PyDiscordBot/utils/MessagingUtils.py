import asyncio

import discord

from PyDiscordBot.misc import Constants


async def convert(ctx):
    return f"Requested by {ctx.author}"


async def embed_basic(ctx, title, description, colour, footer: bool, footercontent=None):
    embed = discord.Embed(title=title, description=description, colour=colour)
    if footer is True:
        if footercontent is None:
            footercontent = await convert(ctx)
        embed.set_footer(text=footercontent)
    return embed


async def message_timechecked(bot, ctx, msg, timeout):
    await msg.add_reaction('✅')
    await msg.add_reaction('❌')

    def check(reaction, user):
        if user == ctx.author and '✅' in str(reaction):
            return True
        if user == ctx.author and '❌' in str(reaction):
            raise asyncio.TimeoutError

    try:
        msg.reactions, user = await bot.wait_for('reaction_add', timeout=timeout, check=check)
        return True
    except asyncio.TimeoutError:
        return False


async def embed_commandFail(ctx, description):
    return await ctx.send(
        embed=await embed_basic(ctx, f"Failed to run {ctx.command}", description, Constants.commandFail, True))
