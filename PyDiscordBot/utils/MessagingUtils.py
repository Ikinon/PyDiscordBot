import asyncio
import re

import discord
from discord.ext import commands

from PyDiscordBot.misc import Constants


def embed_basic(ctx, title, description, colour, footer: bool, footercontent=None) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, colour=colour)
    if footer is True:
        if footercontent is None:
            footercontent = f"Requested by {ctx.author}"
        embed.set_footer(text=footercontent)
    return embed


async def message_timechecked(bot, ctx, msg, timeout) -> bool:
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


async def message_timecheckednumbers(bot: commands.Bot, ctx: commands.Context, msg: discord.Message, nummax: int,
                                     timeout: int, remove_after: bool = False):
    """

    :param bot: bot instance
    :param ctx: command context
    :param msg: msg to add/check reactions on
    :param nummax: max emoji's to check on (limit: 9)
    :param timeout: timeout on author clicking
    :param remove_after: remove the reactions after check complete
    """
    if nummax > 9:
        raise ValueError("argument 'nummax' should be lower than 9")

    for x, z in zip(range(0, nummax), range(1, nummax + 1)):
        asyncio.create_task(msg.add_reaction(f'{z}\N{combining enclosing keycap}'))

    def check_reaction(reaction):
        search = re.search("[0-9](?:\\N{combining enclosing keycap})", str(reaction))
        if search:
            return search.group()[0]

    def check(reaction, user):
        if user == ctx.author:
            return check_reaction(reaction)

    async def remove_reactions(ctx, m):
        m = await ctx.fetch_message(m.id)  # renew cache, we just added new reactions so its not in instance
        if m.channel.permissions_for(ctx.me).manage_messages:
            await m.clear_reactions()
        else:
            for reaction in m.reactions:
                await reaction.remove(ctx.me)

    try:
        msg.reactions, user = await bot.wait_for('reaction_add', timeout=timeout, check=check)
        if remove_after:
            asyncio.get_event_loop().create_task(remove_reactions(ctx, msg))
        return int(check_reaction(msg.reactions))
    except asyncio.TimeoutError:
        if remove_after:
            asyncio.get_event_loop().create_task(remove_reactions(ctx, msg))
        return False


# Returns configured embed
def embed_command_success(ctx, title, description) -> discord.Embed:
    return embed_basic(ctx, title, description, Constants.commandSuccess, True)


def embed_command_info(ctx, title, description) -> discord.Embed:
    return embed_basic(ctx, title, description, Constants.commandInfo, True)


def embed_command_warning(ctx, title, description) -> discord.Embed:
    return embed_basic(ctx, title, description, Constants.commandWarning, True)


def embed_command_fail(ctx, title, description) -> discord.Embed:
    return embed_basic(ctx, title, description, Constants.commandFail, True)


def embed_command_error(ctx, title, description) -> discord.Embed:
    return embed_basic(ctx, title, description, Constants.commandError, True)


# Returns sent Messages
async def send_embed_command_success(ctx, title, description) -> discord.Message:
    return await ctx.send(embed=embed_command_success(ctx, title, description))


async def send_embed_command_info(ctx, title, description) -> discord.Message:
    return await ctx.send(embed=embed_command_info(ctx, title, description))


async def send_embed_command_warning(ctx, title, description) -> discord.Message:
    return await ctx.send(embed=embed_command_warning(ctx, title, description))


async def send_embed_command_fail(ctx, title, description) -> discord.Message:
    return await ctx.send(embed=embed_command_fail(ctx, title, description))


async def send_embed_command_error(ctx, title, description) -> discord.Message:
    return await ctx.send(embed=embed_command_error(ctx, title, description))
