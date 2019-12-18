import discord
from discord.ext import commands

from PyDiscordBot.misc import Constants
from PyDiscordBot.utils import MessagingUtils, DataUtils


class Utils():

    async def __convert(self, ctx, argument=None):
        ret = f'{ctx.author}: {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret

    async def __runchecks(self, bot, ctx, target):
        embed = await MessagingUtils.embed_commandWarning(ctx, "", "")
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

    async def __modlog(self, ctx, target, reason):
        if await self.__modlog_status(ctx) is False:
            return
        elif await self.__modlog_status(ctx):
            embed = await MessagingUtils.embed_basic(ctx, f"{ctx.command}'ed member",
                                                     f"{ctx.author.mention} {ctx.command}ed member {target}",
                                                     Constants.commandInfo, False)
            embed.add_field(name="Channel", value=f"{ctx.channel.name} ({ctx.channel.id})")
            embed.add_field(name="Reason", value=reason)
            modlog = await self.__modlog_status(ctx)
            channel = discord.utils.get(ctx.guild.channels, id=int(modlog[0]))
            if modlog[1] == "ALL":
                await channel.send(embed=embed)
            if str(ctx.command) in modlog[1]:
                await channel.send(embed=embed)

    async def __modlog_status(self, ctx):
        modlog_status = DataUtils.guilddata(ctx.guild.id).get('self.__modlog_status')
        if modlog_status == "NONE":
            return False
        elif modlog_status:
            return [DataUtils.guilddata(ctx.guild.id).get('self.__modlog_channel'), self.__modlog_status]

    async def __create_role(self, ctx, name, permissions: discord.permissions, reason=None):
        return await ctx.guild.__create_role(name=name, permissions=permissions, reason=reason)

    async def kick(self, bot, ctx, member: discord.Member, reason):
        if await self.__runchecks(bot, ctx, member.id):
            reason = await self.__convert(ctx, reason)
            await member.kick(reason=reason)
            await MessagingUtils.send_embed_commandSuccess(ctx, f"Kicked member", f"{member} has been kicked!")
            await self.__modlog(ctx, member, reason)

    async def ban(self, bot, ctx, member: discord.Member, reason):
        if await self.__runchecks(bot, ctx, member.id):
            reason = await self.__convert(ctx, reason)
            await member.ban(reason=reason)
            await MessagingUtils.send_embed_commandSuccess(ctx, "Banned Member", f"{member} has been banned")
            await self.__modlog(ctx, member, reason)

    async def softban(self, bot, ctx, member: discord.Member, reason):
        if await self.__runchecks(bot, ctx, member.id):
            reason = await self.__convert(ctx, reason)
            await member.ban(reason=reason), await member.unban(reason=reason)
            await MessagingUtils.send_embed_commandSuccess(ctx, f"Soft-banned member",
                                                           f"{member} has been soft-banned!")
            await self.__modlog(ctx, member, reason)

    async def unban(self, ctx, user, reason):
        bans = await ctx.guild.bans()
        reason = await self.__convert(ctx, reason)
        for ban in bans:
            if ban.user.name == str(user) or str(ban.user.id) == str(user):
                await ctx.guild.unban(ban.user, reason=reason)
                await MessagingUtils.send_embed_commandSuccess(ctx, f"Unbanned User", f"{ban.user} has been unbanned")
        await self.__modlog(ctx, user, reason)

    # TODO: Timed mute
    async def mute(self, bot, ctx, member, reason):
        if await self.__runchecks(bot, ctx, member.id):
            reason = await self.__convert(ctx, reason)
            embed = await MessagingUtils.embed_commandSuccess(ctx, "Muted Member", f"{member} has been muted!")
            try:
                role = discord.utils.get(ctx.guild.roles, id=int(DataUtils.guilddata(ctx.guild.id).get('mute_role')))
                if role is None: raise AttributeError
            except AttributeError:
                if ctx.guild.me.guild_permissions.manage_channels is False:
                    raise discord.ext.commands.BotMissingPermissions(['manage_channels'])
                role = await self.__create_role(ctx, "Muted", discord.Permissions(permissions=0))
                DataUtils.database().update_one(dict({'_id': ctx.guild.id}),
                                                dict({'$set': {"mute_role": str(role.id)}}))
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
            if role not in member.roles:
                await member.add_roles(role, reason=reason)
            if role in member.roles:
                await member.remove_roles(role, reason=reason)
                embed.description = f"{member} has be un-muted"
                ctx.command = "un-mute"
            if isinstance(member.voice, discord.member.VoiceState):
                if member.voice.channel.permissions_for(ctx.guild.me).mute_members is True:
                    await member.edit(mute=True)
                    embed.add_field(name="Voice Mute", value=f"{member} has also been muted in voice.")
            await ctx.send(embed=embed)
            await self.__modlog(ctx, member, reason)

    # TODO: Warnings: Allow removing warnings
    async def warn(self, bot, ctx, member, reason):
        if await self.__runchecks(bot, ctx, member.id):
            reason = await self.__convert(ctx, reason)
            warnings = []
            try:
                warnings = DataUtils.guilddata(ctx.guild.id).get('warnings').get(str(member.id))
            except AttributeError:
                DataUtils.database().update_one(dict({'_id': ctx.guild.id}),
                                                dict({'$set': {'warnings': {str(member.id): [reason]}}}))
            else:
                warnings.append(reason)
                DataUtils.database().update_many(dict({'_id': ctx.guild.id}),
                                                 dict({'$set': {'warnings': {str(member.id): warnings}}}))

            embed = await MessagingUtils.embed_commandSuccess(ctx, "Warned member", f"{member} has been warned")
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Total Warnings", value=len(warnings))
            await ctx.send(embed=embed)
            await self.__modlog(ctx, member, reason)

    async def memberwarnings(self, bot, ctx, member):
        if await self.__runchecks(bot, ctx, member.id):
            warnings = '\n'.join(DataUtils.guilddata(ctx.guild.id).get('warnings').get(str(member.id)))
            await MessagingUtils.send_embed_commandInfo(ctx, f"Warnings for {member}", warnings)
