from typing import Union

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
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a member from the server"""
        await ModUtils.Utils(self.bot, ctx).kick(member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, target: Union[discord.Member, int], *, reason=None):
        """Bans a user from the server"""
        if isinstance(target, discord.Member):
            await ModUtils.Utils(self.bot, ctx).ban(target, reason)
        if isinstance(target, int):
            await ModUtils.Utils(self.bot, ctx).forceban(target, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason=None):
        """Bans then unbans a member from the server"""
        await ModUtils.Utils(self.bot, ctx).softban(member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user, *, reason=None):
        """Unbans a user from the server"""
        await ModUtils.Utils(self.bot, ctx).unban(user, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        """Mutes a member so they cannot type or speak"""
        await ModUtils.Utils(self.bot, ctx).mute(member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        """Warn a member"""
        await ModUtils.Utils(self.bot, ctx).warn(member, reason)

    @commands.group(name="warnings", invoke_without_command=True)
    @commands.guild_only()
    async def warnings(self, ctx, member: discord.Member):
        """Get warnings for a member"""
        await ModUtils.Utils(self.bot, ctx).memberwarnings(member)

    @warnings.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warnings_remove(self, ctx, member: discord.Member, warning_id: int, reason=None):
        """<member> <warning_id> Remove warnings for a member"""
        await ModUtils.Utils(self.bot, ctx).remove_warning(member, warning_id)

    @warnings.command(name="clear")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warnings_clear(self, ctx, member: discord.Member, reason=None):
        """<member> [reason] Clears all warnings from a member"""
        await ModUtils.Utils(self.bot, ctx).clear_warnings(member, reason)


def setup(bot):
    bot.add_cog(Moderation(bot))
