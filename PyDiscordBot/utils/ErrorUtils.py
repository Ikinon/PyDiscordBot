import sys
import traceback

import discord
from aiohttp import ClientSession
from discord.ext import commands

from PyDiscordBot.utils import MessagingUtils, DataUtils


class ErrorUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Triggered when as an error is raised processing a command."""

        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        # TODO: Find a neat way to make this more specific, such as what the user inputted to make the target unknown
        elif isinstance(error, discord.errors.NotFound):
            return await MessagingUtils.send_embed_commandFail(ctx, f"{ctx.command}", "Could not find target")

        elif isinstance(error, discord.ext.commands.MissingPermissions):
            if (await DataUtils.guild_settings(ctx.guild, "showPermErrors", get_setting_value=True))[0]:
                await MessagingUtils.send_embed_commandFail(ctx, "Missing Permissions",
                                                            f"You need the permission(s) {''.join(error.missing_perms)} for {ctx.command}!")
            return

        elif isinstance(error, discord.ext.commands.BotMissingPermissions):
            return await MessagingUtils.send_embed_commandFail(ctx, "Missing Permissions",
                                                               f"I am missing the permission(s) {''.join(error.missing_perms)} for {ctx.command}!")

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__)
        trace_error = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        err = f"Author: {ctx.author.name}({ctx.author.id})\nMessage: {ctx.message.content}"
        if ctx.guild:
            err += f"\nGuild: {ctx.guild.name}({ctx.guild.id})\n\n{trace_error}"
        elif not ctx.guild:
            err += f"Guild: No guild\n\n{trace_error}"

        async with ClientSession() as session:
            async with session.post('https://hasteb.in/documents', data=''.join(''.join(err))) as post:
                await MessagingUtils.send_embed_commandError(ctx,
                                                             "There was an error while running the command!",
                                                             f"Stack Trace: https://hasteb.in/" +
                                                             (await post.json())['key'])
                if await DataUtils.configData("webhook"):
                    webhook = discord.Webhook.from_url(await DataUtils.configData("webhook"),
                                                       adapter=discord.AsyncWebhookAdapter(session))
                    await webhook.send(err)


def setup(bot):
    bot.add_cog(ErrorUtils(bot))
