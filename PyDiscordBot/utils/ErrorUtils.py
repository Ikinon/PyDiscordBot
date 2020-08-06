import sys
import traceback

import discord
from aiohttp import ClientSession
from discord.ext import commands

from PyDiscordBot.utils import MessagingUtils, DataUtils, CommandUtils


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

        if isinstance(error, commands.NoPrivateMessage):
            return await MessagingUtils.send_embed_commandFail(ctx, "",
                                                               f"{ctx.command} cannot be run in private messages.")

        # TODO: Find a neat way to make this more specific, such as what the user inputted to make the target unknown
        elif isinstance(error, discord.errors.NotFound):
            return await MessagingUtils.send_embed_commandFail(ctx, f"{str(ctx.command).title()}",
                                                               "Could not find target")

        elif isinstance(error, commands.MissingRequiredArgument):
            return await MessagingUtils.send_embed_commandFail(ctx, f"{str(ctx.command).title()}",
                                                               f"Missing required argument `{error.param.name}`")

        elif isinstance(error, commands.BadArgument):
            return await MessagingUtils.send_embed_commandFail(ctx, f"{str(ctx.command).title()}", f"`{error.args[0]}`")

        elif isinstance(error, discord.ext.commands.MissingPermissions):
            guild_data = (await DataUtils.guild_data(ctx.guild.id))
            if guild_data.get("devPermOverride") is not None:
                if await CommandUtils.Checks.User(ctx.author).is_developer():
                    return await ctx.reinvoke()
            if (await DataUtils.guild_settings(ctx.guild, "showPermErrors", guild_data.get("guild_settings"),
                                               get_setting_value=True))[0]:
                return await MessagingUtils.send_embed_commandFail(ctx, "Missing Permissions",
                                                                   f"You need the permission(s) {''.join(error.missing_perms)} for {ctx.command}!")

        elif isinstance(error, discord.ext.commands.BotMissingPermissions):
            return await MessagingUtils.send_embed_commandFail(ctx, "Missing Permissions",
                                                               f"I am missing the permission(s) {''.join(error.missing_perms)} for {ctx.command}!")

        elif isinstance(error, commands.CheckAnyFailure) or isinstance(error, commands.CheckFailure):
            if ctx.command.module != 'PyDiscordBot.commands.Developer':
                return await MessagingUtils.send_embed_commandFail(ctx, "Check failure",
                                                                   f" failed requirements to run `{ctx.command}`")

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__)
        trace_error = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        err = f"Author: {ctx.author.name}({ctx.author.id})\nMessage: {ctx.message.content}"
        if ctx.guild:
            err += f"\nGuild: {ctx.guild.name}({ctx.guild.id})\n\n{trace_error}"
        elif not ctx.guild:
            err += f"\nGuild: No guild\n\n{trace_error}"

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
