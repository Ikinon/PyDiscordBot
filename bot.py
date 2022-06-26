import asyncio
import os

from discord import Intents
from discord.ext import commands

from PyDiscordBot.utils import DataUtils

intents = Intents.default()
# Restricted intent
intents.members = True
intents.presences = True
# Disabling default
intents.typing = False
intents.bans = False
intents.webhooks = False
intents.invites = False


class Bot(commands.Bot):

    async def get_prefix(bot, message):
        return DataUtils.prefix(message.guild)

    async def load_events(self):
        await self.wait_until_ready()
        events = await DataUtils.load_future_events(self)
        print(f"Done loading {events} future actions")

    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, intents=intents)
        print("Loading future actions")
        asyncio.ensure_future(self.load_events(), loop=self.loop)
        self.load_plugins()
        print(f"Loaded {len(self.extensions)} extensions")

    def load_plugins(self):
        for r, d, f in os.walk("PyDiscordBot/"):
            for file in f:
                if str(file).endswith(".py"):
                    file = r + "." + file
                    for c in (("/", "."), ("\\", ".")): file = file.replace(*c)
                    try:
                        self.load_extension(f"{file.strip('.py')}")
                    except Exception as e:
                        if not isinstance(e, commands.NoEntryPointError):
                            print("{0}: {1}".format(type(e).__name__, e))

    async def on_ready(self):
        print(f"Connected as: {self.user} - {self.user.id}\n")

    async def on_message(self, message):
        pass  # I need this for the on_message in events for some reason


bot = Bot().run(DataUtils.config_data("token"))
