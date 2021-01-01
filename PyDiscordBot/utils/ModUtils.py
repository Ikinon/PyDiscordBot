import asyncio
import datetime
from typing import Union

import discord
from discord.ext import commands

from PyDiscordBot.misc import Constants
from PyDiscordBot.utils import MessagingUtils, DataUtils, TimeUtils


class Utils:
    def __init__(self, bot: commands.Bot, ctx: commands.Context, to_send: discord.Embed = None,
                 target: Union[discord.Member, discord.User] = None, reason: str = None, no_modlog: bool = False):
        self.ctx = ctx
        self.no_modlog = no_modlog
        self.bot = bot
        self.reply = to_send
        self.target = target
        self.reason = reason

    async def runchecks(self, target: Union[discord.User, discord.Member], send_reply: bool = True) -> bool:
        embed = await MessagingUtils.embed_commandWarning(self.ctx, "", "")
        if target is None:
            embed.description = "I cannot find that user!"
            if send_reply:
                await self.ctx.send(embed=embed)
            return False
        if target == self.ctx.author:
            embed.description = f"You cannot {self.ctx.command} yourself!"
            if send_reply:
                await self.ctx.send(embed=embed)
            return False
        if target == self.bot.user:
            embed.description = f"I'm not going to {self.ctx.command} myself!"
            if send_reply:
                await self.ctx.send(embed=embed)
            return False
        if self.ctx.guild.get_member(target.id):
            if target == self.ctx.guild.owner:
                embed.description = f"I cannot {self.ctx.command} the owner of the server!"
                if send_reply:
                    await self.ctx.send(embed=embed)
                return False
            if target.top_role > self.ctx.author.top_role and self.ctx.author != self.ctx.guild.owner:
                embed.description = f"Your role is lower than {target.name} in role hierarchy!"
                if send_reply:
                    await self.ctx.send(embed=embed)
                return False
            if target.top_role >= self.ctx.guild.me.top_role:
                embed.description = f"My top role is not higher than {target.name} in role hierarchy!"
                if send_reply:
                    await self.ctx.send(embed=embed)
                return False
        return True

    async def __reason_convert(self, argument=None) -> str:
        ret = ""
        if argument is None:
            ret = f'{self.ctx.author}: No reason given'
        elif argument:
            ret = f'{self.ctx.author}: {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret

    async def __modlog(self, target, reason):
        modlog = await Actions(self.bot, self.ctx).modlog_status()
        if modlog is False:
            return
        elif modlog:
            embed = await MessagingUtils.embed_basic(self.ctx, f"{str(self.ctx.command).title()}",
                                                     f"{self.ctx.author.mention} {str(self.ctx.command).title()} member {target}",
                                                     Constants.commandInfo, False)
            embed.add_field(name="Channel", value=f"{self.ctx.channel.name} ({self.ctx.channel.id})")
            embed.add_field(name="Reason", value=reason)
            channel = discord.utils.get(self.ctx.guild.channels, id=int(modlog[0]))
            if modlog[1] == "ALL" or (str(self.ctx.command) in modlog[1]):
                await channel.send(embed=embed)

    def send_modlog(self):
        if not self.no_modlog:
            asyncio.get_event_loop().create_task(self.__modlog(self.target, self.reason))

    def send_reply(self):
        asyncio.get_event_loop().create_task(self.ctx.send(embed=self.reply))

    def send_modlog_reply(self):
        asyncio.get_event_loop().create_task(self.ctx.send(embed=self.reply))
        if not self.no_modlog:
            asyncio.get_event_loop().create_task(self.__modlog(self.target, self.reason))


class Actions:

    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self.ctx = ctx

    async def __reason_convert(self, argument=None) -> str:
        ret = ""
        if argument is None:
            ret = f'{self.ctx.author}: No reason given'
        elif argument:
            ret = f'{self.ctx.author}: {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret

    async def __create_role(self, name, permissions: discord.permissions, reason=None) -> discord.Role:
        return await self.ctx.guild.create_role(name=name, permissions=permissions, reason=reason)

    async def modlog_status(self) -> Union[list, bool]:
        modlog_status = DataUtils.guild_data(self.ctx.guild.id).get('modlog_status')
        if modlog_status == "NONE":
            return False
        elif modlog_status:
            return [DataUtils.guild_data(self.ctx.guild.id).get('modlog_channel'), modlog_status]

    async def update_modlog_status(self, value) -> None:
        DataUtils.guild_database.update_one(dict({'_id': self.ctx.guild.id}),
                                            dict({'$set': {"modlog_status": value}}))

    async def update_modlog_channel(self, value: int) -> None:
        DataUtils.guild_database.update_one(dict({'_id': self.ctx.guild.id}),
                                            dict({'$set': {"modlog_channel": value}}))

    async def kick(self, member: discord.Member, reason=None):
        reason = await self.__reason_convert(reason)
        await member.kick(reason=reason)
        reply = await MessagingUtils.embed_commandSuccess(self.ctx, f"Kicked member", f"{member} has been kicked")
        return Utils(self.bot, self.ctx, reply, target=member, reason=reason)

    async def ban(self, member: discord.Member, reason=None):
        reason = await self.__reason_convert(reason)
        await member.ban(reason=reason)
        reply = await MessagingUtils.embed_commandSuccess(self.ctx, f"Ban member", f"{member} has been banned")
        return Utils(self.bot, self.ctx, reply, member, reason)

    async def softban(self, member: discord.Member, reason=None):
        reason = await self.__reason_convert(reason)
        await member.ban(reason=reason), await member.unban(reason=reason)
        reply = await MessagingUtils.embed_commandSuccess(self.ctx, f"Soft-banned member",
                                                          f"{member} has been soft-banned")
        return Utils(self.bot, self.ctx, reply, member, reason)

    async def forceban(self, user, reason=None):
        user = await self.bot.fetch_user(user)
        reason = await self.__reason_convert(reason)
        await self.ctx.guild.ban(user, reason=reason)
        reply = await MessagingUtils.embed_commandSuccess(self.ctx, f"Force ban user", f"{user} has been banned")
        return Utils(self.bot, self.ctx, reply, user, reason)

    async def unban(self, user, reason=None):
        bans = await self.ctx.guild.bans()
        reason = await self.__reason_convert(reason)
        for ban in bans:
            if ban.user.name == str(user) or str(ban.user.id) == str(user):
                user = ban.user
                await self.ctx.guild.unban(ban.user, reason=reason)
        reply = await MessagingUtils.embed_commandSuccess(self.ctx, f"Unban user", f"{user} has been un-banned")
        return Utils(self.bot, self.ctx, reply, user, reason)

    async def mute(self, member: discord.Member, reason: str = None):
        reason = await self.__reason_convert(reason)
        embed = await MessagingUtils.embed_commandSuccess(self.ctx, "Mute Toggle", f"{member} has been muted.\nUntil: \u267E"'')
        try:
            role = discord.utils.get(self.ctx.guild.roles, id=
            (await DataUtils.guild_settings(self.ctx.guild, 'mute_role', get_setting_value=True))[0])
            if role is None: raise AttributeError
        except AttributeError:
            if self.ctx.guild.me.guild_permissions.manage_channels is False:
                raise discord.ext.commands.BotMissingPermissions(['manage_channels'])
            role = await self.__create_role("Muted", discord.Permissions(permissions=0), reason)
            await DataUtils.guild_settings(self.ctx.guild, "mute_role", value=role.id, change=True, insert_new=True,
                                           setting_subset="moderation", check_value_type=False)
            failed = 0
            for channel in self.ctx.guild.channels:
                try:
                    if type(channel) == discord.channel.TextChannel:
                        await channel.set_permissions(role, send_messages=False)
                    if type(channel) == discord.channel.VoiceChannel:
                        await channel.set_permissions(role, speak=False)
                except discord.Forbidden:
                    failed = +1
            if failed != 0 & len(self.ctx.guild.channels) != failed:
                embed.add_field(name="Permission Error",
                                value=f"Failed to create channel permission entries for {failed} channel(s).\n Please check permissions.")
        if role in member.roles:
            await member.remove_roles(role, reason=reason)
            await DataUtils.guild_moderation(self.ctx.guild, member, "muted", remove=True)
            embed.description = f"{member} has been un-muted"
            self.ctx.command = "un-mute"
        else:
            await member.add_roles(role, reason=reason)
            await DataUtils.guild_moderation(self.ctx.guild, member, "muted", change=True, value=True)
        if isinstance(member.voice, discord.member.VoiceState):
            if member.voice.channel.permissions_for(self.ctx.guild.me).mute_members:
                if self.ctx.command == "un-mute":
                    await member.edit(mute=False)
                else:
                    await member.edit(mute=True)
                embed.add_field(name="Voice Mute", value=f"{embed.description}")
        return Utils(self.bot, self.ctx, embed, member, reason)

    async def tempmute(self, member: discord.Member, unmute_at: datetime.timedelta, reason: str = None):
        await self.mute(member, reason)
        unmute_at_datetime = datetime.datetime.today() + unmute_at
        await DataUtils.create_future_event(self.bot, self.ctx.guild, self.ctx.author, self.ctx.channel,
                                            unmute_at_datetime, "unmute", [member.id])
        until_date = TimeUtils.human_readable_datetime(unmute_at_datetime)
        time_until = TimeUtils.human_readable_time(int(unmute_at.total_seconds()))
        embed = await MessagingUtils.embed_commandSuccess(self.ctx, "Muted Member",
                                                          f"{member} has been muted\n Until {until_date} (in {time_until})")
        return Utils(self.bot, self.ctx, embed, member, await self.__reason_convert(reason))

    async def warn(self, member, reason: str = None):
        reason = await self.__reason_convert(reason)
        try:
            warnings = DataUtils.guild_data(self.ctx.guild.id).get('guild_moderation').get(
                str(member.id)).get("warnings")
            if warnings is None: raise AttributeError
        except AttributeError:
            warnings = [reason]
            await DataUtils.guild_moderation(self.ctx.guild, member, "warnings", change=True, value=[reason])
        else:
            warnings.append(reason)
            await DataUtils.guild_moderation(self.ctx.guild, member, "warnings", change=True, value=warnings)
        embed = await MessagingUtils.embed_commandSuccess(self.ctx, "Warn Member", f"{member} has been warned")
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="Total Warnings", value=len(warnings))
        return Utils(self.bot, self.ctx, embed, member, reason)

    async def remove_warning(self, member, warning_id: int, reason: str = None):
        reason = await self.__reason_convert(reason)
        warnings = (await DataUtils.guild_moderation(self.ctx.guild, member, "warnings", get_values=True))
        del warnings[warning_id - 1]  # -1 because 0 index
        await DataUtils.guild_moderation(self.ctx.guild, member, "warnings", change=True, value=warnings)
        embed = await MessagingUtils.embed_commandSuccess(self.ctx, "",
                                                          f"Warning with id {warning_id} has been removed from {member}")
        embed.add_field(name="Reason", value=reason)
        return Utils(self.bot, self.ctx, embed, member, reason)

    async def clear_warnings(self, member, reason):
        await DataUtils.guild_moderation(self.ctx.guild, member, "warnings", remove=True)
        embed = await MessagingUtils.embed_commandSuccess(self.ctx, "", f"All warnings have been cleared from {member}")
        embed.add_field(name="Reason", value=reason)
        return Utils(self.bot, self.ctx, embed, member, reason)

    async def memberwarnings(self, member):
        try:
            warnings = (await DataUtils.guild_moderation(self.ctx.guild, member, "warnings", get_values=True))
            # AttributeError: nothing related in database, None: when no key, 0: when list(key type) is empty
            if warnings is None or len(warnings) == 0: raise AttributeError
        except AttributeError:
            embed = await MessagingUtils.embed_commandInfo(self.ctx, f"Warnings for {member}",
                                                           f"{member.name} has no warnings")
            return Utils(self.bot, self.ctx, embed, member, await self.__reason_convert())
        # TODO: Should be a way to make this tidier, do that
        to_send = []
        id = 1
        for warn in warnings:
            to_send.append(f"`{id}`: {warn}\n")
            id += 1
        embed = await MessagingUtils.embed_commandInfo(self.ctx, f"Warnings for {member}", ''.join(to_send))
        return Utils(self.bot, self.ctx, embed, member, await self.__reason_convert())
