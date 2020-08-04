from typing import Union

import discord
from discord.ext import commands

from PyDiscordBot.misc import Constants
from PyDiscordBot.utils import MessagingUtils, DataUtils


class Utils():

    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.ctx = ctx
        self.bot = bot

    async def reason_convert(self, argument=None) -> str:
        ret = ""
        if argument is None:
            ret = f'{self.ctx.author}: No reason given'
        elif argument:
            ret = f'{self.ctx.author}: {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret

    async def __runchecks(self, target: Union[discord.User, discord.Member]) -> bool:
        embed = await MessagingUtils.embed_commandWarning(self.ctx, "", "")
        if target is None:
            embed.description = "I cannot find that user!"
            await self.ctx.send(embed=embed)
            return False
        if target == self.ctx.author:
            embed.description = f"You cannot {self.ctx.command} yourself!"
            await self.ctx.send(embed=embed)
            return False
        if target == self.bot.user:
            embed.description = f"I'm not going to {self.ctx.command} myself!"
            await self.ctx.send(embed=embed)
            return False
        if self.ctx.guild.get_member(target.id):
            if target == self.ctx.guild.owner:
                embed.description = f"I cannot {self.ctx.command} the owner of the server!"
                await self.ctx.send(embed=embed)
                return False
            if target.top_role > self.ctx.author.top_role and self.ctx.author != self.ctx.guild.owner:
                embed.description = f"Your role is lower than {target.name} in role hierarchy!"
                await self.ctx.send(embed=embed)
                return False
            if target.top_role > self.ctx.guild.me.top_role:
                embed.description = f"My top role is lower than {target.name} in role hierarchy!"
                await self.ctx.send(embed=embed)
                return False
        return True

    async def __modlog(self, target, reason):
        modlog = await self.modlog_status()
        if modlog is False:
            return
        elif modlog:
            embed = await MessagingUtils.embed_basic(self.ctx, f"{str(self.ctx.command).title()} member",
                                                     f"{self.ctx.author.mention} {str(self.ctx.command).title()} member {target}",
                                                     Constants.commandInfo, False)
            embed.add_field(name="Channel", value=f"{self.ctx.channel.name} ({self.ctx.channel.id})")
            embed.add_field(name="Reason", value=reason)
            channel = discord.utils.get(self.ctx.guild.channels, id=int(modlog[0]))
            if modlog[1] == "ALL":
                await channel.send(embed=embed)
            if str(self.ctx.command) in modlog[1]:
                await channel.send(embed=embed)

    async def __mod_action_complete(self, target, reason, embed: discord.Embed = None):
        await self.__modlog(target, reason)
        if not embed:
            await MessagingUtils.send_embed_commandSuccess(self.ctx, f"{str(self.ctx.command).title()} User",
                                                           f"Action taken against {target}")
        elif embed:
            await self.ctx.send(embed=embed)

    async def __create_role(self, name, permissions: discord.permissions, reason=None) -> discord.Role:
        return await self.ctx.guild.create_role(name=name, permissions=permissions, reason=reason)

    async def modlog_status(self):
        modlog_status = (await DataUtils.guild_data(self.ctx.guild.id)).get('modlog_status')
        if modlog_status == "NONE":
            return False
        elif modlog_status:
            return [(await DataUtils.guild_data(self.ctx.guild.id)).get('modlog_channel'), modlog_status]

    async def update_modlog_status(self, value):
        (await DataUtils.guild_database()).update_one(dict({'_id': self.ctx.guild.id}),
                                                      dict({'$set': {"modlog_status": value}}))

    async def update_modlog_channel(self, value: int):
        (await DataUtils.guild_database()).update_one(dict({'_id': self.ctx.guild.id}),
                                                      dict({'$set': {"modlog_channel": value}}))

    async def kick(self, member: discord.Member, reason=None):
        if await self.__runchecks(member):
            reason = await self.reason_convert(reason)
            await member.kick(reason=reason)
            await self.__mod_action_complete(member, reason)

    async def ban(self, member: discord.Member, reason=None):
        if await self.__runchecks(member):
            reason = await self.reason_convert(reason)
            await member.ban(reason=reason)
            await self.__mod_action_complete(member, reason)

    async def softban(self, member: discord.Member, reason=None):
        if await self.__runchecks(member):
            reason = await self.reason_convert(reason)
            await member.ban(reason=reason), await member.unban(reason=reason)
            await MessagingUtils.send_embed_commandSuccess(self.ctx, f"Soft-banned member",
                                                           f"{member} has been soft-banned!")
            await self.__modlog(member, reason)

    async def forceban(self, user, reason=None):
        user = await self.bot.fetch_user(user)
        reason = await self.reason_convert(reason)
        if await self.__runchecks(user):
            await self.ctx.guild.ban(user, reason=reason)
            await self.__mod_action_complete(user, reason)

    async def unban(self, user, reason=None):
        bans = await self.ctx.guild.bans()
        reason = await self.reason_convert(reason)
        for ban in bans:
            if ban.user.name == str(user) or str(ban.user.id) == str(user):
                await self.ctx.guild.unban(ban.user, reason=reason)
        await self.__mod_action_complete(user, reason)

    # TODO: Timed mute
    async def mute(self, member: discord.Member, reason: str = None):
        if await self.__runchecks(member):
            reason = await self.reason_convert(reason)
            embed = await MessagingUtils.embed_commandSuccess(self.ctx, "Mute Toggle", f"{member} has been muted")
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
                                    value=f"Failed to create channel permission entries for {failed} channel(s). Please check permissions.")
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
            await self.__mod_action_complete(member, reason, embed)

    # TODO: Allow removing warnings
    async def warn(self, member, reason: str = None):
        if await self.__runchecks(member):
            reason = await self.reason_convert(reason)
            try:
                warnings = (await DataUtils.guild_data(self.ctx.guild.id)).get('guild_moderation').get(
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
            await self.__mod_action_complete(member, reason, embed)

    async def remove_warning(self, member, warning_id: int, reason: str = None):
        warnings = (await DataUtils.guild_moderation(self.ctx.guild, member, "warnings", get_values=True))
        del warnings[warning_id - 1]  # -1 because 0 index
        await DataUtils.guild_moderation(self.ctx.guild, member, "warnings", change=True, value=warnings)
        await MessagingUtils.send_embed_commandSuccess(self.ctx, "",
                                                       f"Warning with id {warning_id} has been removed from {member}")
        await self.__modlog(member, reason=await self.reason_convert(reason))

    async def clear_warnings(self, member, reason: str = None):
        await DataUtils.guild_moderation(self.ctx.guild, member, "warnings", remove=True)
        await MessagingUtils.send_embed_commandSuccess(self.ctx, "", f"All warnings have been cleared from {member}")
        await self.__modlog(member, reason=await self.reason_convert(reason))

    async def memberwarnings(self, member):
        try:
            warnings = (await DataUtils.guild_moderation(self.ctx.guild, member, "warnings", get_values=True))
            # AttributeError: nothing related in database, None: when no key, 0: when list(key type) is empty
            if warnings is None or len(warnings) == 0: raise AttributeError
        except AttributeError:
            return await MessagingUtils.send_embed_commandInfo(self.ctx, f"Warnings for {member}", f"{member.name} has no warnings")
        # TODO: Should be a way to make this tidier, do that
        to_send = []
        id = 1
        for warn in warnings:
            to_send.append(f"`{id}`: {warn}\n")
            id += 1
        await MessagingUtils.send_embed_commandInfo(self.ctx, f"Warnings for {member}", ''.join(to_send))
