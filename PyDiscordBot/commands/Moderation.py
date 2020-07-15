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
    async def kick(self, ctx, member: discord.Member, reason=None):
        await ModUtils.Utils().kick(self.bot, ctx, member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason=None):
        await ModUtils.Utils().ban(self.bot, ctx, member, reason)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            args = ctx.message.content.split()
            msg = await MessagingUtils.send_embed_commandInfo(ctx, "Ban Fail",
                                                              f"{args[1]} was not found in guild, do you want to try "
                                                              f"forceban?")
            if await MessagingUtils.message_timechecked(self.bot, ctx, msg, 10):
                await ModUtils.Utils().forceban(ctx, self.bot, args[1], args[2])

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, reason=None):
        await ModUtils.Utils().softban(self.bot, ctx, member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user, reason=None):
        await ModUtils.Utils.unban(ctx, user, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, reason=None):
        await ModUtils.Utils().mute(self.bot, ctx, member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, reason=None):
        await ModUtils.Utils().warn(self.bot, ctx, member, reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warnings(self, ctx, member: discord.Member):
        await ModUtils.Utils().memberwarnings(self.bot, ctx, member)


def setup(bot):
    bot.add_cog(Moderation(bot))
