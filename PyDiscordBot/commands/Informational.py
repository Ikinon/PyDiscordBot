import discord
from discord.ext import commands

from PyDiscordBot.misc import Constants
from PyDiscordBot.utils import MessagingUtils


class Informational(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def userinfo(self, ctx, user=None):
        """Retrieves information about a user """
        if user is None:
            user = ctx.author
        elif user.isdecimal() is False:
            user: discord.User = await commands.UserConverter().convert(ctx, user)
        elif user.isdecimal():
            user = await self.bot.fetch_user(user)
        embed = await MessagingUtils.embed_commandInfo(ctx, f"{user}", "")
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="User ID", value=user.id, inline=True)
        embed.add_field(name="User Created", value=user.created_at.date(), inline=True)
        if user in ctx.guild.members:
            member = ctx.guild.get_member(user.id)
            embed.add_field(name="Status", value=member.status, inline=True)
            embed.add_field(name="Joined At", value=member.joined_at.date(), inline=True)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(name="guildinfo", aliases=["serverinfo"])
    async def guildinfo(self, ctx, guild: discord.Guild = None):
        """Returns information about the guild"""
        if guild is None:
            guild = ctx.guild
        embed = await MessagingUtils.embed_basic(ctx, f"{guild.name}", "", Constants.commandInfo, True,
                                                 f"ID: {guild.id}")
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Owner", value=guild.owner, inline=True)
        embed.add_field(name="Region", value=guild.region, inline=True)
        embed.add_field(name="Created at", value=guild.created_at.date())
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Informational(bot))
