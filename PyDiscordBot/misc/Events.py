from discord.ext import commands

from PyDiscordBot.utils import DataUtils


async def after_invoke(ctx):
    for x in DataUtils.database().find(dict({'_id': ctx.guild.id})): x
    if bool(x.get('deleteCommand')) is True:
        try:
            await ctx.message.delete()
        except:
            pass


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        toinsert = [
            {"_id": guild.id, "guild_id": guild.id, "modlog_status": "NONE", "deleteCommand": True}
        ]
        DataUtils.database().insert_many(toinsert)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        await after_invoke(ctx)


def setup(bot):
    bot.add_cog(Events(bot))
