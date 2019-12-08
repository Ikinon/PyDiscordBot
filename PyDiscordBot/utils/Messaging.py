import discord


class FooterOpt(str):
    async def convert(self, ctx, argument):
        print(argument)
        if len(argument) == 0:
            return f"Requested by {ctx.author}"
        else:
            return argument


async def embed_basic(title, description, colour, footer: bool, footercontent: FooterOpt = None):
    embed = discord.Embed(title=title, description=description, colour=colour)
    if footer is True:
        embed.set_footer(text=footercontent)
    return embed
