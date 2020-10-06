import asyncio
from contextlib import suppress

import discord
from discord.ext import commands

from PyDiscordBot.utils import DataUtils


async def after_invoke(ctx):
    if ctx.guild is not None:
        if (await DataUtils.guild_settings(ctx.guild, 'deleteCommand', get_setting_value=True))[0]:
            if ctx.command.module != 'PyDiscordBot.commands.Developer':
                with suppress(Exception):  # Oh well, no perms
                    await ctx.message.delete()


async def before_invoke(message):
    try:
        if message.author.id in await DataUtils.configData('developer_id'):
            return True
        blocked_db = DataUtils.blocked_database()
        if (DataUtils.blocked_data(message.author.id, blocked_db)).get('state'):
            return False
        elif message.guild is not None:
            if (DataUtils.blocked_data(message.guild.id, blocked_db)).get('state'):
                return False
        else:
            return True
    except AttributeError:
        return True


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        toinsert = [
            {"_id": guild.id, "guild_id": guild.id, "modlog_status": "NONE", "guild_settings":
                {"general": {"deleteCommand": False, "showPermErrors": True, "prefixOnMention": True},
                 "moderation": {"mute_role": 0, "muteOnRejoin": True}}, }]
        DataUtils.guild_database.insert_many(toinsert)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if (await DataUtils.guild_settings(member.guild, "muteOnRejoin", get_setting_value=True))[0]:
            if await DataUtils.guild_moderation(member.guild, member, "muted", get_values=True):
                with suppress(AttributeError, discord.Forbidden):  # No role/no perms, whatever
                    await member.add_roles(member.guild.get_role(
                        (await DataUtils.guild_settings(member.guild, "mute_role", get_setting_value=True))[0]),
                        reason="AutoMod: Member was previously muted.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        context = await self.bot.get_context(message)
        if context.guild is None or context.guild.me.permissions_in(context.channel).send_messages:
            if context.command is not None:
                if await before_invoke(message):
                    return await asyncio.gather(self.bot.invoke(context), after_invoke(context))

            if self.bot.user in message.mentions:
                if (await DataUtils.guild_settings(message.guild, "prefixOnMention", get_setting_value=True))[0]:
                    return await message.channel.send(f"Prefix is: `{await DataUtils.prefix(message.guild)}`")


def setup(bot):
    bot.add_cog(Events(bot))
