import json
from distutils.util import strtobool
from typing import Union, Any

import discord
import pymongo

with open("config.json") as raw_cfg:
    config = json.load(raw_cfg)


async def configData(data):
    return config[data]


raw_db = pymongo.MongoClient(config["database"])


async def guild_database() -> pymongo.collection.Collection:
    return raw_db["database"]["guilds"]


async def guild_data(guild_id: int, database: pymongo.collection.Collection = None) -> dict:
    if database is None:
        database = (await guild_database())
    for x in database.find(dict({'_id': guild_id})):
        return x


async def blocked_database() -> pymongo.collection.Collection:
    return raw_db["database"]["blocked_ids"]


async def blocked_data(id: int, database: pymongo.collection.Collection = None) -> dict:
    if database is None:
        database = (await blocked_database())
    for x in database.find(dict({'_id': id})):
        return x


async def prefix(prefix_location: discord.Guild = None, change: bool = False, new_prefix: str = None) -> str:
    """

    :param prefix_location: Guild to retrieve/change prefix in, or if None return default
    :param change: Specify if to change the prefix
    :param new_prefix: Max length is 5 characters and must be ascii (except spaces & quotes), if None, prefix is reset
    :return: Prefix
    """
    if prefix_location is not None:
        if change is False:
            guild_prefix = (await guild_data(prefix_location.id)).get("prefix")
            if guild_prefix is not None:
                return guild_prefix
            if guild_prefix is None:
                default_prefix = await configData("prefix")
                (await guild_database()).update_one(dict({'_id': prefix_location.id}),
                                                    dict({'$set': {'prefix': default_prefix}}))
                return default_prefix
        elif change is True:
            if new_prefix is None:
                default_prefix = await configData("prefix")
                (await guild_database()).update_one(dict({'_id': prefix_location.id}),
                                                    dict({'$set': {'prefix': default_prefix}}))
                return default_prefix
            disallowed = [' ', "\"", "\'"]
            if len(new_prefix) <= 5 and new_prefix.isascii() and not any(char in new_prefix for char in disallowed):
                (await guild_database()).update_one(dict({'_id': prefix_location.id}),
                                                    dict({'$set': {'prefix': new_prefix}}))
                return new_prefix
            elif new_prefix:
                raise ValueError(
                    "argument 'new_prefix' should be ascii (except spaces & quotes) and no more than 5 characters")

    if prefix_location is None:
        return await configData("prefix")


async def guild_settings(guild: discord.Guild, setting, settings: Union[discord.Guild, dict] = None, value: Any = None,
                         get_setting_subset: bool = False, get_setting_value: bool = False, check_value: bool = False,
                         change: bool = False, setting_subset: str = None, insert_new: bool = False,
                         check_value_type: bool = True) -> tuple:
    """

    :param guild: Retrieve/Append setting information from
    :param setting: Setting to Retrieve/Change/Append to guild
    :param settings: Source of settings, provide a dict or retrieve from guild
    :param value: Value of setting(key)
    :param get_setting_subset: return Subset of given setting
    :param get_setting_value: return Value of given setting
    :param check_value: return True/False if given value is aligned with current guild settings
    :param change: Specify if setting should be changed with given value
    :param setting_subset: Subset for setting to go into, unspecified it will go into where it currently is
    :param insert_new: If setting should be inserted if not present (REQUIRES setting_subset)
    :param check_value_type: Check if value is same type as old value (DOESN'T work with insert_new)
    """
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


async def guild_moderation(guild: discord.Guild, user: Union[discord.Member, discord.User], custom: str,
                           get_values: bool = False, change: bool = False, value=None, remove: bool = False):
    """

    :param guild: Retrieve/Append moderation values from
    :param user: User to query
    :param custom: Moderation key, example as 'warnings'
    :param get_values: Return current value of key
    :param change: Specify if key should be changed (if remove is True, this is automatically True)
    :param value: New value for key
    :param remove: Remove value for key (value unnecessary)
    """
    operator = ""
    if remove is False:
        operator = '$set'
    elif remove is True:
        operator = '$unset'
    if change is True or remove is True:
        if remove is True and value is None:
            value = True  # Just need anything here
        (await guild_database()).update_one(dict({'_id': guild.id}),
                                            dict({operator: {f'guild_moderation.{str(user.id)}.{custom}': value}}))
    if get_values:
        return (await guild_data(guild.id)).get('guild_moderation').get(str(user.id)).get(custom)
