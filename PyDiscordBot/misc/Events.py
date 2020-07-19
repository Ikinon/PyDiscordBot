from discord.ext import commands

from PyDiscordBot.utils import DataUtils


async def after_invoke(ctx):
    if DataUtils.guilddata(ctx.guild.id).get('deleteCommand') is True:
        if ctx.command.module != 'PyDiscordBot.commands.Owner':
            try:
                await ctx.message.delete()
            except:
                pass


async def before_invoke(message):
    try:
        if DataUtils.blockeddata(message.author.id).get('state'):
            return False
        if message.guild is not None:
            if DataUtils.blockeddata(message.guild.id).get('state'):
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
            {"_id": guild.id, "guild_id": guild.id, "modlog_status": "NONE", "deleteCommand": True}
        ]
        DataUtils.guild_database().insert_many(toinsert)

    @commands.Cog.listener()
    async def on_message(self, message):
        if await before_invoke(message):
            await self.bot.process_commands(message)
            await after_invoke(await self.bot.get_context(message))


def setup(bot):
    bot.add_cog(Events(bot))
