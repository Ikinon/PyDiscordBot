import json
from distutils.util import strtobool

import aiofiles
import pymongo

from PyDiscordBot.utils import MessagingUtils


async def configData(data):
    async with aiofiles.open("config.json", mode="r") as f:
        return (json.loads(await f.read()))[data]


async def raw_db():
    return pymongo.MongoClient(await configData("database"))


async def guild_database():
    return (await raw_db())["database"]["guilds"]


async def guild_data(guild_id):
    for x in (await guild_database()).find(dict({'_id': guild_id})):
        return x


async def blocked_database():
    return (await raw_db())["database"]["blocked_ids"]


async def blocked_data(id):
    for x in (await blocked_database()).find(dict({'_id': id})):
        return x


async def settingChanger(ctx, blacklist, Guildsettings, setting, value):
    if setting in blacklist:
        await MessagingUtils.send_embed_commandWarning(ctx, "Setting Change",
                                                       "You are not allowed to modify this setting.")
    if setting not in Guildsettings and setting not in blacklist:
        await MessagingUtils.send_embed_commandFail(ctx, "Setting Change", f"{setting} does not exist.")
    if setting in Guildsettings and setting not in blacklist:
        Oldvalue = (await guild_data(ctx.guild.id)).get(setting)
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
            (await guild_database()).update_one(dict({'_id': ctx.guild.id}), dict({'$set': {setting: value}}))
            embed = await MessagingUtils.embed_commandSuccess(ctx, "Setting Change", "New setting applied")
            embed.add_field(name=f"Old setting for {setting}", value=Oldvalue, inline=False)
            embed.add_field(name=f"New setting for {setting}", value=value, inline=False)
            await ctx.send(embed=embed)
