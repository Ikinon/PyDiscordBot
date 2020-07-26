from discord.ext import commands

from PyDiscordBot.utils import MessagingUtils, ModUtils, DataUtils


class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx, setting=None, value=None):
        blacklist = ['_id', 'guild_id', 'warnings', 'modlog_status', 'modlog_channel']
        guildSettings = []
        for x in (await DataUtils.guild_data(ctx.guild.id)):
            if x not in blacklist:
                guildSettings.append(x)
        if not setting:
            embed = await MessagingUtils.embed_commandInfo(ctx, f"Settings for guild {ctx.guild}", "")
            for item in guildSettings:
                embed.add_field(name=item, value=DataUtils.guild_data(ctx.guild.id).get(item), inline=False)
            await ctx.send(embed=embed)
        else:
            await DataUtils.settingChanger(ctx, blacklist, guildSettings, setting, value)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def modlog(self, ctx, cmds=None, channel=None):
        if cmds is not None:
            mod_cmds = [str(x) for x in (self.bot.get_cog("Moderation").get_commands()) + ["un-mute", "ALL", "NONE"]]
            if ',' in cmds:
                if set(cmds).issubset(mod_cmds):
                    await ModUtils.Utils(self.bot, ctx).update_modlog_status(cmds)
                elif set(cmds):
                    return await MessagingUtils.send_embed_commandWarning(ctx, f"{ctx.command} Settings",
                                                                          f"1+ of {cmds} are not commands, commands are:\n {' '.join(mod_cmds)}")
            elif cmds:
                if cmds in mod_cmds:
                    await ModUtils.Utils(self.bot, ctx).update_modlog_status(cmds)
                elif cmds:
                    return await MessagingUtils.send_embed_commandWarning(ctx, f"{ctx.command} Settings",
                                                                          f"{cmds} is not a command, commands are:\n {' '.join(mod_cmds)}")
        if channel is not None:
            await ModUtils.Utils(self.bot, ctx).update_modlog_channel(int(channel))
        settings = await ModUtils.Utils(self.bot, ctx).modlog_status()
        embed = await MessagingUtils.embed_commandInfo(ctx, "modlog Settings", "")
        if settings is not False:
            embed.add_field(name="Commands under modlog", value=' '.join(settings[1]), inline=False)
            embed.add_field(name="Channel ID", value=settings[0], inline=False)
        if settings is False:
            embed.description = "Disabled"
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Management(bot))
