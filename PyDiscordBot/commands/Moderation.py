import discord
from discord.ext import commands

from PyDiscordBot.utils import ModUtils, MessagingUtils


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await ModUtils.Utils(self.bot, ctx).kick(member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await ModUtils.Utils(self.bot, ctx).ban(member, reason)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            args = ctx.message.content.split()
            msg = await MessagingUtils.send_embed_commandInfo(ctx, "Ban Fail",
                                                              f"{args[1]} was not found in guild, do you want to try "
                                                              f"forceban?")
            if await MessagingUtils.message_timechecked(self.bot, ctx, msg, 10):
                reason = ""
                if len(args) < 3:
                    reason = await ModUtils.Utils(self.bot, ctx).reason_convert()
                await ModUtils.Utils(self.bot, ctx).forceban(args[1], reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason=None):
        await ModUtils.Utils(self.bot, ctx).softban(member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user, *, reason=None):
        await ModUtils.Utils(self.bot, ctx).unban(user, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        await ModUtils.Utils(self.bot, ctx).mute(member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        await ModUtils.Utils(self.bot, ctx).warn(member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warnings(self, ctx, member: discord.Member):
        await ModUtils.Utils(self.bot, ctx).memberwarnings(member)


def setup(bot):
    bot.add_cog(Moderation(bot))
