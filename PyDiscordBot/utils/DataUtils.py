import json

import pymongo

from distutils.util import strtobool

from PyDiscordBot.utils import MessagingUtils

with open("config.json") as cfg:
    config = json.load(cfg)

client = pymongo.MongoClient(config["database"])


def config(data):
    return config[data]


def database():
    return client["database"]["guilds"]


def guilddata(guild_id):
    for x in database().find(dict({'_id': guild_id})):
        return x


async def settingChanger(ctx, blacklist, Guildsettings, setting, value):
    if setting in blacklist:
        await MessagingUtils.send_embed_commandWarning(ctx, "Setting Change",
                                                       "You are not allowed to modify this setting.")
    if setting not in Guildsettings and setting not in blacklist:
        await MessagingUtils.send_embed_commandFail(ctx, "Setting Change", f"{setting} does not exist.")
    if setting in Guildsettings and setting not in blacklist:
        Oldvalue = guilddata(ctx.guild.id).get(setting)
        try:
            # TODO: This needs to be more accurate, for example, if the setting is a channel id, make sure it exists!
            if type(Oldvalue) is bool:  # I hope there's another decent way to try to do this
                value = bool(strtobool(value))
            if type(Oldvalue) is not bool:
                value = Oldvalue(value)
        except ValueError:
            await MessagingUtils.send_embed_commandWarning(ctx, "Setting Change", f"New value is not the correct type, "
                                                                                  f"old value was {type(Oldvalue)},{value} is {type(value)}")
        else:
            database().update_one(dict({'_id': ctx.guild.id}), dict({'$set': {setting: value}}))
            embed = await MessagingUtils.embed_commandSuccess(ctx, "Setting Change", "New setting applied")
            embed.add_field(name=f"Old setting for {setting}", value=Oldvalue, inline=False)
            embed.add_field(name=f"New setting for {setting}", value=value, inline=False)
            await ctx.send(embed=embed)
