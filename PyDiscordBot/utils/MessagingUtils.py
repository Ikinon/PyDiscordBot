import discord


async def convert(ctx):
    return f"Requested by {ctx.author}"


async def embed_basic(ctx, title, description, colour, footer: bool, footercontent= None):
    embed = discord.Embed(title=title, description=description, colour=colour)
    if footer is True:
        if footercontent is None:
            footercontent= await convert(ctx)
        embed.set_footer(text=footercontent)
    return embed
