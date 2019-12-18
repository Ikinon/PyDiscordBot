import discord
from discord.ext import commands

from PyDiscordBot.misc import Constants
from PyDiscordBot.utils import MessagingUtils


class Informational(commands.Cog):

    def __converter(self, ctx):
        if str(ctx.command) == 'userinfo': return ctx.author
        if str(ctx.command) == 'guildinfo': return ctx.guild

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def userinfo(self, ctx, user: discord.User = None):
        if user is None:
            user = self.__converter(ctx)
        embed = await MessagingUtils.embed_commandInfo(ctx, f"{user}", "")
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="User ID", value=user.id, inline=True)
        embed.add_field(name="User Created", value=user.created_at.date(), inline=True)
        if user in self.bot.users:
            embed.add_field(name="Status", value=user.status, inline=True)
            embed.add_field(name="Joined At", value=user.joined_at.date(), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="guildinfo", aliases=["serverinfo"])
    async def guildinfo(self, ctx, guild: discord.Guild = None):
        if guild is None:
            guild = self.__converter(ctx)
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
