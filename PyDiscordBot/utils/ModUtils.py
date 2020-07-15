import discord
from discord.ext import commands

from PyDiscordBot.misc import Constants
from PyDiscordBot.utils import MessagingUtils, DataUtils


class Utils():

    def __init__(self, bot, ctx):
        self.ctx = ctx
        self.bot = bot

    async def reason_convert(self, argument=None):
        ret = f'{self.ctx.author}: {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret

    async def __runchecks(self, target):
        embed = await MessagingUtils.embed_commandWarning(self.ctx, "", "")
        if target is None:
            embed.description = "I cannot find that user!"
            await self.ctx.send(embed=embed)
            return False
        if target == self.ctx.author.id:
            embed.description = f"You cannot {self.ctx.command} yourself!"
            await self.ctx.send(embed=embed)
            return False
        if target == self.bot.user.id:
            embed.description = f"I'm not going to {self.ctx.command} myself!"
            await self.ctx.send(embed=embed)
            return False
        elif target:
            return True

    async def __modlog(self, target, reason):
        if await self.modlog_status() is False:
            return
        elif await self.modlog_status():
            embed = await MessagingUtils.embed_basic(self.ctx, f"{self.ctx.command}'ed member",
                                                     f"{self.ctx.author.mention} {self.ctx.command}ed member {target}",
                                                     Constants.commandInfo, False)
            embed.add_field(name="Channel", value=f"{self.ctx.channel.name} ({self.ctx.channel.id})")
            embed.add_field(name="Reason", value=reason)
            modlog = await self.modlog_status()
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

    async def __create_role(self, name, permissions: discord.permissions, reason=None):
        return await self.ctx.guild.create_role(name=name, permissions=permissions, reason=reason)

    async def modlog_status(self):
        modlog_status = DataUtils.guilddata(self.ctx.guild.id).get('modlog_status')
        if modlog_status == "NONE":
            return False
        elif modlog_status:
            return [DataUtils.guilddata(self.ctx.guild.id).get('modlog_channel'), modlog_status]

    async def update_modlog_status(self, value):
        DataUtils.database().update_one(dict({'_id': self.ctx.guild.id}), dict({'$set': {"modlog_status": value}}))

    async def update_modlog_channel(self, value: int):
        DataUtils.database().update_one(dict({'_id': self.ctx.guild.id}), dict({'$set': {"modlog_channel": value}}))

    async def kick(self, member: discord.Member, reason=None):
        if await self.__runchecks(member.id):
            reason = await self.reason_convert(reason)
            await member.kick(reason=reason)
            await self.__mod_action_complete(member, reason)

    async def ban(self, member: discord.Member, reason=None):
        if await self.__runchecks(member.id):
            reason = await self.reason_convert(reason)
            await member.ban(reason=reason)
            await self.__mod_action_complete(member, reason)

    async def softban(self, member: discord.Member, reason=None):
        if await self.__runchecks(member.id):
            reason = await self.reason_convert(reason)
            await member.ban(reason=reason), await member.unban(reason=reason)
            await MessagingUtils.send_embed_commandSuccess(self.ctx, f"Soft-banned member",
                                                           f"{member} has been soft-banned!")
            await self.__modlog(member, reason)

    async def forceban(self, user, reason=None):
        user = await self.bot.fetch_user(user)
        reason = await self.reason_convert(reason)
        if await self.__runchecks(user.id):
            await self.ctx.guild.ban(user, reason=reason)
            await self.__mod_action_complete(user, reason)

    async def unban(self, user, reason=None):
        bans = await self.ctx.guild.bans()
        reason = await self.reason_convert(reason)
        for ban in bans:
            if ban.user.name == str(user) or str(ban.user.id) == str(user):
                await self.ctx.guild.unban(ban.user, reason=reason)
        await self.__mod_action_complete(user, reason)

    # TODO: Timed mute, Voice Mute
    # TODO: BUG: This doesn't work when the member in in a voice chat?!
    async def mute(self, member, reason):
        if await self.__runchecks(member.id):
            reason = await self.reason_convert(reason)
            embed = await MessagingUtils.embed_commandSuccess(self.ctx, "Muted Member", f"{member} has been muted!")
            try:
                role = discord.utils.get(self.ctx.guild.roles, id=int(DataUtils.guilddata(self.ctx.guild.id).get('mute_role')))
                if role is None: raise AttributeError
            except AttributeError:
                if self.ctx.guild.me.guild_permissions.manage_channels is False:
                    raise discord.ext.commands.BotMissingPermissions(['manage_channels'])
                role = await self.__create_role(self.ctx, "Muted", discord.Permissions(permissions=0))
                DataUtils.database().update_one(dict({'_id': self.ctx.guild.id}),
                                                dict({'$set': {"mute_role": str(role.id)}}))
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
                                    value=f"Failed to crate channel permission entries for {failed} channel(s). Please check permissions.")
            if role not in member.roles:
                await member.add_roles(role, reason=reason)
            if role in member.roles:
                await member.remove_roles(role, reason=reason)
                embed.description = f"{member} has been un-muted"
                embed.title="Un-Muted Member"
                self.ctx.command = "un-mute"
            await self.__mod_action_complete(member, reason, embed)

    # TODO: Allow removing warnings
    async def warn(self, member, reason=None):
        if await self.__runchecks(member.id):
            reason = await self.reason_convert(reason)
            warnings = []
            try:
                warnings = DataUtils.guilddata(self.ctx.guild.id).get('warnings').get(str(member.id))
            except AttributeError:
                DataUtils.database().update_one(dict({'_id': self.ctx.guild.id}),
                                                dict({'$set': {'warnings': {str(member.id): [reason]}}}))
            else:
                warnings.append(reason)
                DataUtils.database().update_many(dict({'_id': self.ctx.guild.id}),
                                                 dict({'$set': {'warnings': {str(member.id): warnings}}}))

            embed = await MessagingUtils.embed_commandSuccess(self.ctx, "Warn User", f"{member} has been warned")
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Total Warnings", value=len(warnings))
            await self.__mod_action_complete(member, reason, embed)

    async def memberwarnings(self, member):
        if await self.__runchecks(member.id):
            warnings = '\n'.join(DataUtils.guilddata(self.ctx.guild.id).get('warnings').get(str(member.id)))
            await MessagingUtils.send_embed_commandInfo(self.ctx, f"Warnings for {member}", warnings)
