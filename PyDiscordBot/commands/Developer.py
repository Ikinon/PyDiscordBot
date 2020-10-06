import io
import textwrap
import traceback
from contextlib import redirect_stdout

import discord
from discord.ext import commands

from PyDiscordBot.utils import DataUtils, CommandUtils, MessagingUtils


class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if await CommandUtils.Checks.User(ctx.author).is_developer():
            return True

    @commands.command(aliases=["exit"])
    async def shutdown(self, ctx):
        msg = await MessagingUtils.send_embed_commandInfo(ctx, "", "Sure?")
        check = await MessagingUtils.message_timechecked(self.bot, ctx, msg, 10)
        if check:
            return await self.bot.logout()
        else:
            await msg.edit(content="Cancelled", embed=None)

    @commands.command(name="loadext")
    async def load_extension(self, ctx, value):
        self.bot.load_extension(value)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command(name="unloadext")
    async def unload_extension(self, ctx, value):
        self.bot.unload_extension(value)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command(name="reloadext")
    async def reload_extension(self, ctx, extension):
        self.bot.reload_extension(extension)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command(name="reloadexts")
    async def reload_extensions(self, ctx):
        for ext in list(map(str, self.bot.extensions)):
            self.bot.reload_extension(ext)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command(name="permoverride")
    async def override_perms(self, ctx, value: bool):
        if value is True:
            DataUtils.guild_database.update_one(dict({'_id': ctx.guild.id}),
                                                dict({'$set': {"devPermOverride": True}}))
        if value is False:
            DataUtils.guild_database.update_one(dict({'_id': ctx.guild.id}),
                                                dict({'$unset': {"devPermOverride": True}}))
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command(name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""
        # Source: https://github.com/Rapptz/RoboDanny/
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
        }

        env.update(globals())

        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @_eval.error
    async def eval_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("Eval something at least smh!")


def setup(bot):
    bot.add_cog(Developer(bot))
