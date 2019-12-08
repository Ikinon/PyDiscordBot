import sys
import traceback

from aiohttp import ClientSession
from discord.ext import commands

from PyDiscordBot.misc import Constants
from PyDiscordBot.utils import Messaging


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

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        # TODO: Only does first line .. ln.36
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__)
        err = traceback.format_exception(type(error), error, error.__traceback__)
        async with ClientSession() as session:
            async with session.post('https://hasteb.in/documents', data=err[0].encode('utf-8')) as post:
                return await ctx.send(embed=await Messaging.embed_basic(ctx, "There was an error while running the command!",
                                                                        f"Stack Trace: https://hasteb.in/" +
                                                                        (await post.json())['key'],
                                                                        Constants.commandError, False))


def setup(bot):
    bot.add_cog(ErrorUtils(bot))
