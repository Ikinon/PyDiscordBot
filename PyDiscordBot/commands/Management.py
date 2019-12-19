from discord.ext import commands

from PyDiscordBot.utils import DataUtils, MessagingUtils


class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        blacklist = ['_id', 'guild_id', 'warnings']
        settings = []
        for x in DataUtils.guilddata(ctx.guild.id):
            if x not in blacklist:
                settings.append(x)
        embed = await MessagingUtils.embed_commandInfo(ctx, f"Settings for guild {ctx.guild}", "")
        for item in settings:
            embed.add_field(name=item, value=DataUtils.guilddata(ctx.guild.id).get(item), inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Management(bot))
