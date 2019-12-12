import discord
from discord.ext import commands

from PyDiscordBot.misc import Constants
from PyDiscordBot.utils import MessagingUtils, DataUtils


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


async def modlog(ctx, target, reason):
    if await check_modlog_status(ctx) is False:
        return
    elif await check_modlog_status(ctx):
        embed = await MessagingUtils.embed_basic(ctx, f"{ctx.command}ed member",
                                                 f"{ctx.author.mention} {ctx.command}ed member {target}",
                                                 Constants.commandInfo, False)
        embed.add_field(name="Channel", value=f"{ctx.channel.name} ({ctx.channel.id})")
        embed.add_field(name="Reason", value=reason)
        modlog = await check_modlog_status(ctx)
        channel = discord.utils.get(ctx.guild.channels, id=int(modlog[0]))
        if modlog[1] == "ALL":
            await channel.send(embed=embed)
        if str(ctx.command) in modlog[1]:
            await channel.send(embed=embed)


async def check_modlog_status(ctx):
    for x in DataUtils.database().find(dict({'_id': ctx.guild.id})): x
    if x.get('modlog_status') == "NONE":
        return False
    elif x.get('modlog_status'):
        temp = [x.get("modlog_channel")]
        temp.append(x.get("modlog_status"))
        return temp


async def create_role(ctx, name, permissions: discord.permissions, reason=None):
    return await ctx.guild.create_role(name=name, permissions=permissions, reason=reason)


async def kick(bot, ctx, member: discord.Member, reason):
    if await runchecks(bot, ctx, member.id):
        reason = await convert(ctx, reason)
        await member.kick(reason=reason)
        await ctx.send(embed=await MessagingUtils.embed_basic(ctx, f"Kicked member", f"{member} has been kicked!",
                                                              Constants.commandSuccess, True))
        await modlog(ctx, member, reason)


async def ban(bot, ctx, member: discord.Member, reason):
    if await runchecks(bot, ctx, member.id):
        reason = await convert(ctx, reason)
        await member.ban(reason=reason)
        await ctx.send(embed=await MessagingUtils.embed_basic(ctx, f"Banned member", f"{member} has been banned!",
                                                              Constants.commandSuccess, True))
        await modlog(ctx, member, reason)


async def softban(bot, ctx, member: discord.Member, reason):
    if await runchecks(bot, ctx, member.id):
        reason = await convert(ctx, reason)
        await member.ban(reason=reason), await member.unban(reason=reason)
        await ctx.send(
            embed=await MessagingUtils.embed_basic(ctx, f"Soft-banned member", f"{member} has been soft-banned!",
                                                   Constants.commandSuccess, True))
        await modlog(ctx, member, reason)


async def unban(ctx, user, reason):
    bans = await ctx.guild.bans()
    reason = await convert(ctx, reason)
    for ban in bans:
        if ban.user.name == str(user) or str(ban.user.id) == str(user):
            await ctx.guild.unban(ban.user, reason=reason)
            await ctx.send(
                embed=await MessagingUtils.embed_basic(ctx, f"Unbanned User", f"{ban.user} has been unbanned",
                                                       Constants.commandSuccess, True))
    await modlog(ctx, user, reason)


# TODO: Timed mute
async def mute(bot, ctx, member, reason):
    if await runchecks(bot, ctx, member.id):
        reason = await convert(ctx, reason)
        embed = await MessagingUtils.embed_basic(ctx, "Muted Member", f"{member} has been muted!",
                                                 Constants.commandSuccess, True)
        for x in DataUtils.database().find(): x
        try:
            role = discord.utils.get(ctx.guild.roles, id=int(x.get('mute_role')))
            if role is None: raise AttributeError
        except AttributeError:
            if ctx.guild.me.guild_permissions.manage_channels is False:
                raise discord.ext.commands.BotMissingPermissions(['manage_channels'])
            role = await create_role(ctx, "Muted", discord.Permissions(permissions=0))
            DataUtils.database().update_one(dict({'_id': ctx.guild.id}), dict({'$set': {"mute_role": str(role.id)}}))
            failed = 0
            for channel in ctx.guild.channels:
                try:
                    if type(channel) == discord.channel.TextChannel:
                        await channel.set_permissions(role, send_messages=False)
                    if type(channel) == discord.channel.VoiceChannel:
                        await channel.set_permissions(role, speak=False)
                except discord.Forbidden:
                    failed = +1
            if failed != 0 & len(ctx.guild.channels) != failed:
                embed.add_field(name="Permission Error",
                                value=f"Failed to crate channel permission entries for {failed} channel(s). Please check permissions.")
        await member.add_roles(role, reason=reason)
        if isinstance(member.voice, discord.member.VoiceState):
            if member.voice.channel.permissions_for(ctx.guild.me).mute_members is True:
                await member.edit(mute=True)
                embed.add_field(name="Voice Mute", value=f"{member} has also been muted in voice.")
        await ctx.send(embed=embed)
        await modlog(ctx, member, reason)
