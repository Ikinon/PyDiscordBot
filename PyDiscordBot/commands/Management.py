from discord.ext import commands

from PyDiscordBot.utils import DataUtils, MessagingUtils, ModUtils


class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx, settingChange=None, value=None):
        blacklist = ['_id', 'guild_id', 'warnings', 'modlog_status', 'modlog_channel']
        settings = []
        for x in DataUtils.guilddata(ctx.guild.id):
            if x not in blacklist:
                settings.append(x)
        if not settingChange:
            embed = await MessagingUtils.embed_commandInfo(ctx, f"Settings for guild {ctx.guild}", "")
            for item in settings:
                embed.add_field(name=item, value=DataUtils.guilddata(ctx.guild.id).get(item), inline=False)
            await ctx.send(embed=embed)
        # Todo: Check if setting is correct type 
        else:
            if settingChange in blacklist:
                await MessagingUtils.send_embed_commandWarning(ctx, "Setting Change",
                                                               "You are not allowed to modify this setting.")
            if settingChange not in settings and settingChange not in blacklist:
                await MessagingUtils.send_embed_commandFail(ctx, "Setting Change", f"{settingChange} does not exist.")
            if settingChange in settings and settingChange not in blacklist:
                previous = DataUtils.guilddata(ctx.guild.id).get(settingChange)
                DataUtils.database().update_one(dict({'_id': ctx.guild.id}), dict({'$set': {settingChange: value}}))
                embed = await MessagingUtils.embed_commandSuccess(ctx, "Setting Change", "New setting applied")
                embed.add_field(name=f"Old setting for {settingChange}", value=previous, inline=False)
                embed.add_field(name=f"New setting for {settingChange}", value=value, inline=False)
                await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def modlog(self, ctx, value=None, channel=None):
        if value is not None:
            if ',' in value: value = value.split(',')
            await ModUtils.Utils().update_modlog_status(ctx, value)
        if channel is not None:
            await ModUtils.Utils().update_modlog_channel(ctx, int(channel))
        if channel is None:
            await ModUtils.Utils().update_modlog_channel(ctx, ctx.channel.id)
        settings = await ModUtils.Utils().modlog_status(ctx)
        embed = await MessagingUtils.embed_commandInfo(ctx, f"modlog Settings for guild {ctx.guild}", "")
        if settings is not False:
            embed.add_field(name="Commands under modlog", value=settings[1], inline=False)
            embed.add_field(name="Channel ID", value=settings[0], inline=False)
        if settings is False:
            embed.description = "modlog disabled"
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Management(bot))
