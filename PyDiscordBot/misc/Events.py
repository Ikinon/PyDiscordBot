import asyncio

import discord
from discord.ext import commands

from PyDiscordBot.utils import DataUtils


async def after_invoke(ctx):
    if (await DataUtils.guild_settings(ctx.guild, 'deleteCommand', get_setting_value=True))[0]:
        if ctx.command.module != 'PyDiscordBot.commands.Developer':
            try:
                await ctx.message.delete()
            except:
                pass


async def before_invoke(message):
    try:
        if message.author.id in await DataUtils.configData('developer_id'):
            return True
        elif (await DataUtils.blocked_data(message.author.id)).get('state'):
            return False
        elif message.guild is not None:
            if (await DataUtils.blocked_data(message.guild.id)).get('state'):
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
                 "moderation": {"mute_role": 0}}, }]
        (await DataUtils.guild_database()).insert_many(toinsert)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        context = await self.bot.get_context(message)
        if context.command is not None:
            if await before_invoke(message):
                return await asyncio.gather(self.bot.invoke(context), after_invoke(context))

        if self.bot.user in message.mentions:
            if (await DataUtils.guild_settings(message.guild, "prefixOnMention", get_setting_value=True))[0]:
                return await message.channel.send(f"Prefix is: `{await DataUtils.prefix(message.guild)}`")


def setup(bot):
    bot.add_cog(Events(bot))
