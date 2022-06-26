from typing import Union

import discord
from discord.ext import commands

from PyDiscordBot.utils import DataUtils


class DecoratorChecks:

    def is_developer(self, ctx: commands.Context = None):
        async def pred(ctx):
            if ctx.author.id in DataUtils.config_data("developer_id"):
                return True
            else:
                return False

        return commands.check(pred(ctx))


class Checks:
    class User:

        def __init__(self, memberuser: Union[discord.Member, discord.User]):
            self.user = memberuser

        async def is_developer(self) -> bool:
            if self.user.id in DataUtils.config_data("developer_id"):
                return True
            else:
                return False
