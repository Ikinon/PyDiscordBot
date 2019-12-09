import discord
from discord.ext import commands

from PyDiscordBot.misc import Constants
from PyDiscordBot.utils import MessagingUtils


async def convert(ctx, argument=None):
    ret = f'{ctx.author}: {argument}'

    if len(ret) > 512:
        reason_max = 512 - len(ret) - len(argument)
        raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
    return ret


async def runchecks(bot, ctx, target):
    embed = await MessagingUtils.embed_basic(ctx, "", "", Constants.commandWarning, True)
    if target is None:
        embed.description = "I cannot find that user!"
        await ctx.send(embed=embed)
        return False
    if target == ctx.author.id:
        embed.description = f"You cannot {ctx.command} yourself!"
        await ctx.send(embed=embed)
        return False
    if target == bot.user.id:
        embed.description = f"I'm not going to {ctx.command} myself!"
        await ctx.send(embed=embed)
        return False
    elif target:
        return True


async def kick(bot, ctx, member: discord.Member, reason):
    if await runchecks(bot, ctx, member.id):
        reason = await convert(ctx, reason)
        await member.kick(reason=reason)
        await ctx.send(embed=await MessagingUtils.embed_basic(ctx, f"Kicked member", f"{member} has been kicked!",
                                                              Constants.commandSuccess, True))


async def ban(bot, ctx, member: discord.Member, reason):
    if await runchecks(bot, ctx, member.id):
        reason = await convert(ctx, reason)
        await member.ban(reason=reason)
        await ctx.send(embed=await MessagingUtils.embed_basic(ctx, f"Banned member", f"{member} has been banned!",
                                                              Constants.commandSuccess, True))
