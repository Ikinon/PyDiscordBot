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
        for x in DataUtils.guild_database(ctx.guild.id):
            if x not in blacklist:
                guildSettings.append(x)
        if not setting:
            embed = await MessagingUtils.embed_commandInfo(ctx, f"Settings for guild {ctx.guild}", "")
            for item in guildSettings:
                embed.add_field(name=item, value=DataUtils.guild_database(ctx.guild.id).get(item), inline=False)
            await ctx.send(embed=embed)
        else:
            await DataUtils.settingChanger(ctx, blacklist, guildSettings, setting, value)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def modlog(self, ctx, value=None, channel=None):
        if value is not None:
            if ',' in value: value = value.split(',')
            await ModUtils.Utils(self.bot, ctx).update_modlog_status(value)
        if channel is not None:
            await ModUtils.Utils(self.bot, ctx).update_modlog_channel(int(channel))
        if channel is None:
            await ModUtils.Utils(self.bot, ctx).update_modlog_channel(ctx.channel.id)
        settings = await ModUtils.Utils(self.bot, ctx).modlog_status()
        embed = await MessagingUtils.embed_commandInfo(ctx, f"modlog Settings for guild {ctx.guild}", "")
        if settings is not False:
            embed.add_field(name="Commands under modlog", value=settings[1], inline=False)
            embed.add_field(name="Channel ID", value=settings[0], inline=False)
        if settings is False:
            embed.description = "modlog disabled"
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Management(bot))
