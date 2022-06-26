from typing import Union

import discord
from discord.ext import commands

from PyDiscordBot.utils import DataUtils


async def unmute(bot: commands.Bot, guild, author, channel, **kwargs):
    guild = bot.get_guild(guild)
    author = guild.get_member(author)
    target: Union[discord.Member, None] = guild.get_member(kwargs.get("extra_args")[0])
    if not target:
        return  # Member left the guild
    mute_role = guild.get_role((await DataUtils.guild_settings(guild, "mute_role", get_setting_value=True))[0])

    await target.remove_roles(mute_role, reason=f"Auto-Unmute of user, action initiated by {author}")


async def add_roles(bot: commands.Bot, guild, author, channel, **kwargs):
    guild = bot.get_guild(guild)
    await guild.chunk()
    target = guild.get_member(kwargs.get("extra_args")[1])
    roles = list(map(lambda x: target.guild.get_role(x), kwargs.get("extra_args")[0]))

    await target.add_roles(*roles, reason=kwargs.get("extra_args")[2])
