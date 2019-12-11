import json

import pymongo
from discord.ext import commands

with open("config.json") as cfg:
    config = json.load(cfg)

client = pymongo.MongoClient(config["database"])
guilddata = client["database"]
guildi = guilddata["guilds"]


def config(data):
    return config[data]


def database():
    return guildi
