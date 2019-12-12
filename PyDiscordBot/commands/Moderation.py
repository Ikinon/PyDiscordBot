import discord
from discord.ext import commands

from PyDiscordBot.utils import ModUtils


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, reason=None):
        await ModUtils.kick(self.bot, ctx, member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason=None):
        await ModUtils.ban(self.bot, ctx, member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, reason=None):
        await ModUtils.softban(self.bot, ctx, member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user, reason=None):
        await ModUtils.unban(ctx, user, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, reason=None):
        await ModUtils.mute(self.bot, ctx, member, reason)


def setup(bot):
    bot.add_cog(Moderation(bot))
