import json
from distutils.util import strtobool
from typing import Union, Any

import aiofiles
import discord
import pymongo


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


async def guild_settings(guild: discord.Guild, setting, settings: Union[discord.Guild, dict] = None, value: Any = None,
                         get_setting_subset: bool = False, get_setting_value: bool = False, check_value: bool = False,
                         change: bool = False, insert_new: bool = False, setting_subset: str = None,
                         check_value_type: bool = True):
    if isinstance(settings, discord.Guild) or settings is None:
        settings = (await guild_data(guild.id)).get("guild_settings")
    subset = None
    to_ret = []
    for item in settings:  # iterating through subsets
        items = settings.get(item)  # subset of item
        for item_setting in items:  # iterating through settings of current subset
            if setting in item_setting:
                subset = item  # subset of current setting
                if get_setting_subset:
                    to_ret.append(item)
                if get_setting_value:
                    to_ret.append(items.get(item_setting))  # setting
    if not insert_new:
        old_value = (settings.get(subset)).get(setting)
    if check_value:
        if old_value is value:
            to_ret.append(True)
        elif old_value:
            to_ret.append(False)
    if change:
        # TODO: This needs to be more accurate, for example, if the setting is a channel id, make sure it exists!
        if check_value_type:
            if type(old_value) is bool:  # I hope there's another decent way to try to do this
                value = bool(strtobool(value))
            if type(old_value) is not bool:
                value = type(old_value)(value)
        if not insert_new:
            settings[subset][setting] = value
        elif insert_new:
            settings[setting_subset][setting] = value

        (await (guild_database())).update_many(dict({'_id': guild.id}), dict({'$set': {'guild_settings': settings}}))
    return tuple(to_ret)
