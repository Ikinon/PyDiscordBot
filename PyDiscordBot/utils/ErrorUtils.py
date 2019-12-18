import sys
import traceback

import discord
from aiohttp import ClientSession
from discord.ext import commands

from PyDiscordBot.utils import MessagingUtils


class ErrorUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Triggered when as an error is raised processing a command."""

        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, discord.ext.commands.MissingPermissions):
            return await MessagingUtils.send_embed_commandFail(ctx, "Missing Permissions",
                                                               f"You need the permission(s) {''.join(error.missing_perms)} for {ctx.command}!")

        elif isinstance(error, discord.ext.commands.BotMissingPermissions):
            return await MessagingUtils.send_embed_commandFail(ctx, "Missing Permissions",
                                                               f"I am missing the permission(s) {''.join(error.missing_perms)} for {ctx.command}!")

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__)
        err = traceback.format_exception(type(error), error, error.__traceback__)
        async with ClientSession() as session:
            async with session.post('https://hasteb.in/documents', data=''.join(''.join(err))) as post:
                return await MessagingUtils.send_embed_commandError(ctx, "There was an error while running the command!",
                                                              f"Stack Trace: https://hasteb.in/" +
                                                              (await post.json())['key'])


def setup(bot):
    bot.add_cog(ErrorUtils(bot))
