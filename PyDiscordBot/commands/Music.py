import itertools
from datetime import timedelta

import discord
import wavelink
from discord.ext import commands

from PyDiscordBot.utils import MessagingUtils, DataUtils, TimeUtils, MusicUtils


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = MusicUtils.WavelinkClient(bot=bot)
        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink_client = self.wavelink
            node_config: dict = DataUtils.config["lavaplayer"]
            self.bot.loop.create_task(self.wavelink.initiate_node(host=node_config.get("host"),
                                                                  port=node_config.get("port"),
                                                                  rest_uri=node_config.get("rest_uri"),
                                                                  identifier=node_config.get("identifier"),
                                                                  password=node_config.get("password"),
                                                                  region="eu_central"))

    @commands.command(name="pause")
    async def pause(self, ctx):
        """Pauses the player"""
        player = self.wavelink.get_player(ctx.guild.id)
        if player.is_paused:
            await player.set_pause(False)
            return await MessagingUtils.send_embed_commandSuccess(ctx, "", "Player Unpaused")
        await player.set_pause(True)
        await MessagingUtils.send_embed_commandSuccess(ctx, "", "Paused playback")

    @commands.command()
    async def play(self, ctx, *, query: str):
        """Plays a track from a query"""
        tracks = await self.wavelink.get_tracks(f'ytsearch:{query}')

        if not tracks:
            return await MessagingUtils.send_embed_commandFail(ctx, "", "Could not find any songs with that query")

        player = self.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self._join)

        await MessagingUtils.send_embed_commandSuccess(ctx, "", f"Added {str(tracks[0])} to queue")
        await player.play(tracks[0])

    @commands.command()
    async def playing(self, ctx):
        """Gets information about the currently playing song"""
        player = self.wavelink.get_player(ctx.guild.id)
        song: wavelink.Track = player.current
        if not song:
            return await MessagingUtils.send_embed_commandInfo(ctx, "", "Not currently playing anything")
        embed = await MessagingUtils.embed_commandInfo(ctx, f"Current track: {str(song)}", "")
        embed.set_thumbnail(url=song.thumb)
        position = TimeUtils.human_readable_time(timedelta(seconds=round(round(player.position) / 1000)).seconds)
        duration = TimeUtils.human_readable_time(timedelta(seconds=round(round(song.duration) / 1000)).seconds)

        embed.description = f"Duration: {position}/{duration}\n" \
                            f"URL: [click]({song.uri})\n" \
                            f"Author: {song.author}\n"
        if player.is_paused:
            embed.description += "\n**Currently paused**"
        await ctx.send(embed=embed)

    @commands.command()
    async def search(self, ctx, *, query: str):
        """Searches youtube for the query"""
        tracks = await self.wavelink.get_tracks(f'ytsearch:{query}')

        if not tracks:
            return await MessagingUtils.send_embed_commandFail(ctx, "", "Could not find any songs with that query")

        embed = await MessagingUtils.embed_commandInfo(ctx, f"Found songs with query {query}", "")
        max = 5
        if len(tracks) < 5:
            max = len(tracks)

        for track, x in zip(itertools.islice(tracks, max), range(1, max+1)):
            embed.description += f"{x}: {track}\n"

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
        """Stops the player and clears the queue"""
        await (self.wavelink.get_player(ctx.guild.id)).destroy()
        await MessagingUtils.send_embed_commandSuccess(ctx, "", "Stopped music")

    @commands.command(name="join", aliases=["connect"])
    async def _join(self, ctx, *, channel: discord.VoiceChannel = None):
        """Joins to a specified channel or the channel the author is connected to"""
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
        """Leaves the channel currently connected to"""
        player = self.wavelink.get_player(ctx.guild.id)
        channel = discord.utils.get(ctx.guild.channels, id=player.channel_id)
        if channel is None:
            return await MessagingUtils.send_embed_commandWarning(ctx, "", "I am not connected to a voice channel")
        await player.disconnect()
        await MessagingUtils.send_embed_commandSuccess(ctx, "", f"Disconnected from voice channel {channel.name}")

        wavelink.WavelinkMixin.listener()

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
