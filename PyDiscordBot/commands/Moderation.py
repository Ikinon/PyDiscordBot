import discord
from discord.ext import commands

from PyDiscordBot.utils import ModUtils, MessagingUtils


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kick(self, ctx, member: discord.Member, reason=None):
        await ModUtils.kick(self.bot, ctx, member, reason)


def setup(bot):
    bot.add_cog(Moderation(bot))
