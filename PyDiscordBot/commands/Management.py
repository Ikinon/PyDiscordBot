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
        guildSettings = (await DataUtils.guild_data(ctx.guild.id)).get("guild_settings")
        embed = await MessagingUtils.embed_commandInfo(ctx, f"Settings for guild {ctx.guild}", "")
        if setting_name is None:
            for item in guildSettings:
                contents = "```"
                items = guildSettings.get(item)  # subset of item
                for setting in items:
                    contents += f"{setting}: {items.get(setting)}\n"
                contents += "```"
                embed.add_field(name=item, value=contents, inline=False)
        else:
            try:
                old_setting = (await DataUtils.guild_settings(ctx.guild, setting_name, settings=guildSettings,
                                                              get_setting_value=True))[0]
                await DataUtils.guild_settings(ctx.guild, setting_name, value=value, change=True)
            except AttributeError:
                return await MessagingUtils.send_embed_commandWarning(ctx, "Setting change",
                                                                      f"{setting_name} is not a valid setting")
            else:
                embed.add_field(name=f"New settings applied for {setting_name}",
                                value=f"Old setting: {old_setting}\nNew setting: {value}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def modlog(self, ctx, cmds=None, channel=None):
        """Retrieve/set modlog settings"""
        if cmds is not None:
            mod_cmds = [str(x) for x in (self.bot.get_cog("Moderation").get_commands()) + ["un-mute", "ALL", "NONE"]]
            if ',' in cmds:
                if set(cmds).issubset(mod_cmds):
                    await ModUtils.Actions(self.bot, ctx).update_modlog_status(cmds)
                elif set(cmds):
                    return await MessagingUtils.send_embed_commandWarning(ctx, f"{ctx.command} Settings",
                                                                          f"1+ of {cmds} are not commands, commands are:\n {' '.join(mod_cmds)}")
            elif cmds:
                if cmds in mod_cmds:
                    await ModUtils.Actions(self.bot, ctx).update_modlog_status(cmds)
                elif cmds:
                    return await MessagingUtils.send_embed_commandWarning(ctx, f"{ctx.command} Settings",
                                                                          f"{cmds} is not a command, commands are:\n {' '.join(mod_cmds)}")
        if channel is not None:
            await ModUtils.Actions(self.bot, ctx).update_modlog_channel(int(channel))
        settings = await ModUtils.Actions(self.bot, ctx).modlog_status()
        embed = await MessagingUtils.embed_commandInfo(ctx, "modlog Settings", "")
        if settings is not False:
            embed.add_field(name="Commands under modlog", value=' '.join(settings[1]), inline=False)
            embed.add_field(name="Channel ID", value=settings[0], inline=False)
        if settings is False:
            embed.description = "Disabled"
        await ctx.send(embed=embed)

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx):
        """Return/Set the guild prefix"""
        await MessagingUtils.send_embed_commandInfo(ctx, "",
                                                    f"Current server prefix is : `{await DataUtils.prefix(ctx.guild)}`")

    @prefix.command(name="change")
    @commands.has_permissions(manage_guild=True)
    async def prefix_change(self, ctx, new_prefix: str):
        """Changes the prefix of the server"""
        current_prefix = await DataUtils.prefix(ctx.guild)
        await DataUtils.prefix(ctx.guild, change=True, new_prefix=new_prefix)
        await MessagingUtils.send_embed_commandInfo(ctx, "", f"New prefix is `{new_prefix}`\n"
                                                             f"(Old prefix was: `{current_prefix}`)")

    @prefix.command(name="reset", aliases=["clear"])
    @commands.has_permissions(manage_guild=True)
    async def prefix_reset(self, ctx):
        """Resets the prefix of the server back to the default"""
        old_prefix = await DataUtils.prefix(ctx.guild)
        prefix = await DataUtils.prefix(ctx.guild, change=True)
        await MessagingUtils.send_embed_commandInfo(ctx, "", f"Prefix reset to: `{prefix}`\n"
                                                             f"(Old prefix was: `{old_prefix}`)")


def setup(bot):
    bot.add_cog(Management(bot))
