import json

import pymongo

with open("config.json") as cfg:
    config = json.load(cfg)

client = pymongo.MongoClient(config["database"])
guilddata = client["database"]
guildi = guilddata["guilds"]


def config(data):
    return config[data]


def database():
    return guildi


def guilddata(guildid):
    for x in database().find(dict({'_id': guildid})):
        return x
