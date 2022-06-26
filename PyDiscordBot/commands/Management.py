from typing import Union

import discord
from discord.ext import commands

from PyDiscordBot.utils import MessagingUtils, ModUtils, DataUtils


class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx, setting_name=None, value=None):
        """Retrieves/sets guild settings"""
        guild_settings = DataUtils.guild_data(ctx.guild.id).get("guild_settings")
        embed = MessagingUtils.embed_command_info(ctx, f"Settings for guild {ctx.guild}", "")
        if setting_name is None:
            for item in guild_settings:
                contents = "```"
                items = guild_settings.get(item)  # subset of item
                for setting in items:
                    contents += f"{setting}: {items.get(setting)}\n"
                contents += "```"
                embed.add_field(name=item, value=contents, inline=False)
        else:
            try:
                old_setting = (await DataUtils.guild_settings(ctx.guild, setting_name, settings=guild_settings,
                                                              get_setting_value=True))[0]
                await DataUtils.guild_settings(ctx.guild, setting_name, value=value, change=True)
            except AttributeError:
                return await MessagingUtils.send_embed_command_warning(ctx, "Setting change",
                                                                       f"{setting_name} is not a valid setting")
            else:
                embed.add_field(name=f"New settings applied for {setting_name}",
                                value=f"Old setting: {old_setting}\nNew setting: {value}")
        await ctx.send(embed=embed)

    @commands.group("autorole", invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, enabled: Union[Union[bool, str], None] = None):
        if isinstance(enabled, str):
            if enabled.lower() == "true":
                enabled = True
            elif enabled.lower() == "false":
                enabled = False
            else:
                raise discord.ext.commands.BadArgument

        setting = enabled
        if not enabled:
            setting = (await DataUtils.guild_settings(ctx.guild, "autorole", get_setting_value=True, value=False,
                                                      setting_subset="moderation", check_value_type=False,
                                                      insert_new=True))[0] or False
        elif enabled:
            await DataUtils.guild_settings(ctx.guild, "autorole", value=enabled, change=True,
                                           setting_subset="moderation", insert_new=True, check_value_type=False)

        try:
            roles = list(map(lambda x: ctx.guild.get_role(x).name,
                             (await DataUtils.guild_management(ctx.guild, "autorole", "roles", get_values=True))))
        except AttributeError:
            roles = None
        await MessagingUtils.send_embed_command_info(ctx, "Autorole Settings",
                                                     f"Enabled: {setting}\nRoles in autorole: {roles}")

    @autorole.command(name="add")
    @commands.has_permissions(administrator=True)
    async def autorole_add_role(self, ctx, role: discord.Role):

        try:
            roles = (await DataUtils.guild_management(ctx.guild, "autorole", "roles", get_values=True))
        except AttributeError:
            roles = []

        if role.id in roles:
            return await MessagingUtils.send_embed_command_warning(ctx, "Autorole",
                                                                   f"Role `{role.name}` is already in autorole!")
        roles.append(role.id)

        await DataUtils.guild_management(ctx.guild, "autorole", "roles", change=True, value=roles)

        roles = list(map(lambda x: ctx.guild.get_role(x).name, roles))
        embed = MessagingUtils.embed_command_success(ctx, "Autorole", "")
        embed.add_field(name="Roles added for autorole", value=f"Roles being added: {roles}")
        await ctx.send(embed=embed)

    @autorole.command("remove")
    @commands.has_permissions(administrator=True)
    async def autorole_remove_role(self, ctx, role: discord.Role):

        try:
            roles = (await DataUtils.guild_management(ctx.guild, "autorole", "roles", get_values=True))
        except AttributeError:
            roles = []

        if role.id not in roles:
            return await MessagingUtils.send_embed_command_warning(ctx, "Autorole",
                                                                   f"Role `{role.name}` is not in autorole!")
        roles.remove(role.id)

        await DataUtils.guild_management(ctx.guild, "autorole", "roles", change=True, value=roles)

        roles = list(map(lambda x: ctx.guild.get_role(x).name, roles))
        embed = MessagingUtils.embed_command_success(ctx, "Autorole", "")
        embed.add_field(name="Roles removed for autorole", value=f"Roles being added: {roles}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def modlog(self, ctx, cmds=None, channel=None):
        """Retrieve/set modlog settings"""
        if cmds is not None:
            mod_cmds = [str(x) for x in
                        (self.bot.get_cog("Moderation").get_commands()) + ["un-mute", "ALL", "NONE"]]
            if ',' in cmds:
                if set(cmds).issubset(mod_cmds):
                    await ModUtils.Actions(self.bot, ctx).update_modlog_status(cmds)
                elif set(cmds):
                    return await MessagingUtils.send_embed_command_warning(ctx, f"{ctx.command} Settings",
                                                                           f"1+ of {cmds} are not commands, commands are:\n {' '.join(mod_cmds)}")
            elif cmds:
                if cmds in mod_cmds:
                    await ModUtils.Actions(self.bot, ctx).update_modlog_status(cmds)
                elif cmds:
                    return await MessagingUtils.send_embed_command_warning(ctx, f"{ctx.command} Settings",
                                                                           f"{cmds} is not a command, commands are:\n {' '.join(mod_cmds)}")
        if channel is not None:
            await ModUtils.Actions(self.bot, ctx).update_modlog_channel(int(channel))
        settings = await ModUtils.Actions(self.bot, ctx).modlog_status()
        embed = MessagingUtils.embed_command_info(ctx, "modlog Settings", "")
        if settings is not False:
            embed.add_field(name="Commands under modlog", value=' '.join(settings[1]), inline=False)
            embed.add_field(name="Channel ID", value=settings[0], inline=False)
        if settings is False:
            embed.description = "Disabled"
        await ctx.send(embed=embed)

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx):
        """Return/Set the guild prefix"""
        await MessagingUtils.send_embed_command_info(ctx, "",
                                                     f"Current server prefix is : `{DataUtils.prefix(ctx.guild)}`")

    @prefix.command(name="change")
    @commands.has_permissions(manage_guild=True)
    async def prefix_change(self, ctx, new_prefix: str):
        """Changes the prefix of the server"""
        current_prefix = DataUtils.prefix(ctx.guild)
        DataUtils.prefix(ctx.guild, change=True, new_prefix=new_prefix)
        await MessagingUtils.send_embed_command_info(ctx, "", f"New prefix is `{new_prefix}`\n"
                                                              f"(Old prefix was: `{current_prefix}`)")

    @prefix.command(name="reset", aliases=["clear"])
    @commands.has_permissions(manage_guild=True)
    async def prefix_reset(self, ctx):
        """Resets the prefix of the server back to the default"""
        old_prefix = DataUtils.prefix(ctx.guild)
        prefix = DataUtils.prefix(ctx.guild, change=True)
        await MessagingUtils.send_embed_command_info(ctx, "", f"Prefix reset to: `{prefix}`\n"
                                                              f"(Old prefix was: `{old_prefix}`)")


def setup(bot):
    bot.add_cog(Management(bot))
