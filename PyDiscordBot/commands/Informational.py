from datetime import datetime
from typing import Union

import discord
from discord.ext import commands

from PyDiscordBot.utils import MessagingUtils


def human_time(time: datetime):
    return time.strftime("%A %d %B %Y at %H:%M UTC")  # day date month year time


class Informational(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def userinfo(self, ctx, *, user=None):
        """Retrieves information about a user """
        if user is None:
            user = ctx.author
        elif user.isdecimal() is False:
            user: discord.User = await commands.UserConverter().convert(ctx, user)
        elif user.isdecimal():
            user = await self.bot.fetch_user(user)
        embed = await MessagingUtils.embed_commandInfo(ctx, f"{user}", "")
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="User ID", value=user.id, inline=False)
        embed.add_field(name="User Created", value=human_time(user.created_at), inline=False)
        if ctx.guild is not None:
            if user in ctx.guild.members:
                member = ctx.guild.get_member(user.id)
                embed.add_field(name="Status", value=member.status, inline=False)
                embed.add_field(name="Joined At", value=human_time(member.joined_at), inline=False)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(name="guildinfo", aliases=["serverinfo"])
    async def guildinfo(self, ctx, *, guild: Union[int, str] = None):
        """Returns information about current/specified guild

        To specify another guild, use guild ID or name (case sensitive)
        NOTE: The bot must be in the target guild to retrieve information about it
        """
        if guild is None:
            guild = ctx.guild
        elif isinstance(guild, int):
            temp = self.bot.get_guild(guild)
            if temp is not None:
                guild = temp
        elif isinstance(guild, str):
            temp = discord.utils.get(self.bot.guilds, name=guild)
            if temp is not None:
                guild = temp
        if isinstance(guild, str) or isinstance(guild, int):
            return await MessagingUtils.send_embed_commandFail(ctx, "", f"Cannot find guild with name/ID `{guild}`")
        created_at = guild.created_at.strftime("%A %d %B %Y at %H:%M UTC")  # Day date month year time
        filter_level = str(guild.explicit_content_filter).replace("_", " ").title()
        verification_level = str(guild.verification_level).title()

        embed = await MessagingUtils.embed_commandInfo(ctx, f"{guild.name}'s infomation.", "")
        embed.set_footer(text=f"Guild ID: {guild.id} | Requested by {ctx.author}")
        embed.set_thumbnail(url=guild.icon_url)
        embed.description = f"`Owner:` {guild.owner}\n`Created on:` {created_at}\n`Members:` {guild.member_count}\n" \
                            f"`Content filter:` {filter_level}\n`Verification level:` {verification_level}\n" \
                            f"`Voice region:` {guild.region}"
        embed.add_field(name="Channels:",
                        value=f"`Text Channels:` {len(guild.text_channels)} | `Voice Channels:` {len(guild.voice_channels)}",
                        inline=False)
        if len(guild.features) != 0:
            field = ""
            for feature in guild.features:
                field += f"\N{WHITE HEAVY CHECK MARK} {str(feature).replace('_', ' ').lower().title()}\n"
            embed.add_field(name="Features:", value=field, inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Informational(bot))
