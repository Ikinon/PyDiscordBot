import asyncio
from typing import Union

import wavelink
from discord.ext import commands
from wavelink import Track

from PyDiscordBot.utils import DataUtils


class WavelinkClient(wavelink.Client):
    class Player(wavelink.Player):

        def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot], guild_id: int, node, **kwargs):
            super().__init__(bot, guild_id, node, **kwargs)
            try:
                asyncio.ensure_future(self.set_volume(DataUtils.guild_data(guild_id).get("music").get("volume")))
            except AttributeError:
                pass

        async def set_volume(self, vol: int) -> None:
            DataUtils.guild_database.update_one(dict({'_id': self.guild_id}),
                                                dict({'$set': {'music.volume': vol}}))
            await super().set_volume(vol)

        async def play(self, track: Track, *, replace: bool = True, start: int = 0, end: int = 0) -> None:
            await super().play(track=track, replace=replace, start=start, end=end)

    def get_player(self, guild_id: int, *, cls=Player, node_id=None, **kwargs):
        return super().get_player(guild_id, cls=cls, node_id=node_id)
