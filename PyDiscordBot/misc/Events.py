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
                {"general": {"deleteCommand": False}, "moderation": {"mute_role": 0}}, }]
        (await DataUtils.guild_database()).insert_many(toinsert)

    @commands.Cog.listener()
    async def on_message(self, message):
        if await before_invoke(message):
            await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        await after_invoke(ctx)


def setup(bot):
    bot.add_cog(Events(bot))
