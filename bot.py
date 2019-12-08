import json
import os

from discord.ext import commands

# config
with open("config.json") as cfg:
    config = json.load(cfg)


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=config["prefix"])

    # Plugin Loader
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
        Bot.load_plugins(self)
        print(f"Bot name: {self.user.name}\n"
              f"Bot ID: {self.user.id}\n"
              "Successful Login")


bot = Bot().run(config["token"])
