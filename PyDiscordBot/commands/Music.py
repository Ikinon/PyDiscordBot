import itertools

import discord
import wavelink
from discord.ext import commands

from PyDiscordBot.utils import MessagingUtils


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = self.wavelink

        self.bot.loop.create_task(self.wavelink.initiate_node(host='127.0.0.1', port=2333,
                                                              rest_uri='http://127.0.0.1:2333',
                                                              password='youshallnotpass',
                                                              identifier='TEST',
                                                              region='us_central'))

    @commands.command(name="pause")
    async def pause(self, ctx):
        player = self.wavelink.get_player(ctx.guild.id)
        if player.is_paused:
            await player.set_pause(False)
            return await MessagingUtils.send_embed_commandWarning(ctx, "", "Player Unpaused")
        await player.set_pause(True)
        await MessagingUtils.send_embed_commandSuccess(ctx, "", "Paused playback")

    @commands.command()
    async def play(self, ctx, *, query: str):
        tracks = await self.bot.wavelink.get_tracks(f'ytsearch:{query}')

        if not tracks:
            return await MessagingUtils.send_embed_commandError(ctx, "", "Could not find any songs with that query")

        player = self.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self._join)

        await ctx.send(f"Added {str(tracks[0])} to queue")
        await player.play(tracks[0])

    @commands.command()
    async def search(self, ctx, *, query: str):
        tracks = await self.wavelink.get_tracks(f'ytsearch:{query}')

        if not tracks:
            return await MessagingUtils.send_embed_commandError(ctx, "", "Could not find any songs with that query")

        embed = await MessagingUtils.embed_commandInfo(ctx, f"Found songs with query {query}", "")
        max = 5
        if len(tracks) < 5:
            max = len(tracks)

        for track in itertools.islice(tracks, max):
            embed.description += f"{track}\n"

        embed.description += f"\n\nPick an item from list"
        msg: discord.Message = await ctx.send(embed=embed)
        resp = await MessagingUtils.message_timecheckednumbers(self.bot, ctx, msg, max, 10, True)
        if not resp:
            return await msg.edit(embed=await MessagingUtils.embed_commandSuccess(ctx, "", f"Search response timeout"))
        await (self.wavelink.get_player(ctx.guild.id)).play(tracks[resp - 1])
        await msg.edit(
            embed=await MessagingUtils.embed_commandSuccess(ctx, "", f"Added {tracks[resp - 1]} to the queue"))

    @commands.command()
    async def stop(self, ctx):
        await (self.wavelink.get_player(ctx.guild.id)).destroy()
        await MessagingUtils.send_embed_commandSuccess(ctx, "", "Stopped music")

    @commands.command(name="join", aliases=["connect"])
    async def _join(self, ctx, *, channel: discord.VoiceChannel = None):
        if not channel:
            if isinstance(ctx.author.voice, discord.member.VoiceState):
                channel = ctx.author.voice.channel
            else:
                return await MessagingUtils.send_embed_commandFail(ctx, "",
                                                                   "Be in a voice channel for me to join or specify "
                                                                   "a channel")
        await (self.wavelink.get_player(ctx.guild.id)).connect(channel.id)
        await MessagingUtils.send_embed_commandSuccess(ctx, "", f"Connected to voice channel {channel.name}")

    @commands.command(name="leave", aliases=["disconnect"])
    async def _leave(self, ctx):
        player = self.wavelink.get_player(ctx.guild.id)
        channel = discord.utils.get(ctx.guild.channels, id=player.channel_id)
        if channel is None:
            return await MessagingUtils.send_embed_commandWarning(ctx, "", "I am not connected to a voice channel")
        await player.disconnect()
        await MessagingUtils.send_embed_commandSuccess(ctx, "", f"Disconnected from voice channel {channel.name}")

    @commands.command(name="volume", aliases=["vol"])
    async def _volume(self, ctx, volume: int = None):
        player = self.wavelink.get_player(ctx.guild.id)
        if not volume:
            return await MessagingUtils.send_embed_commandInfo(ctx, "", f"Volume is currently at {player.volume}")
        if volume > 1000 or volume < 0:
            return await MessagingUtils.send_embed_commandWarning(ctx, "", "Volume must be between 0 and 1000")

        await player.set_volume(volume)
        await MessagingUtils.send_embed_commandSuccess(ctx, "", f"Adjusting player volume to {volume}.")


def setup(bot):
    bot.add_cog(Music(bot))
