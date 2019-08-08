import json
import os

from discord.ext import commands

# config
with open("config.json") as cfg:
    config = json.load(cfg)


# Plugin loader
def load_plugins():
    for p in os.listdir("PyDiscordBot/commands"):
        if p.endswith(".py"):
            p = p.rstrip(".py")
            try:
                bot.load_extension(f'plugins.{p}')
            except Exception as error:
                exc = "{0}: {1}".format(type(error).__name__, error)


class bot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=config["prefix"])

    async def on_ready(self):
        load_plugins()
        print(f"Bot name: {self.user.name}\n"
              f"Bot ID: {self.user.id}\n"
              "Successful Login")


bot = bot().run(config["token"])
