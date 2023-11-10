# import async_timeout
# import disnake
# import wavelink
# from disnake import ClientException
# from disnake.ext import commands
# from wavelink import SoundCloudTrack
# from wavelink.ext import spotify
# from wavelink.ext.spotify import SpotifyTrack
#
# from src.utils.player import DisPlayer, voice_channel_player, voice_connected, Provider, MustBeSameChannel
# from src.utils.misc import Paginator
# import asyncio
import disnake
from disnake.ext import commands
from disnake.abc import GuildChannel
import disnake.utils
from disnake.ui import View
from wavelink.ext import spotify
import wavelink
import datetime
from disnake import Interaction, ChannelType


class queueView(View):

    @disnake.ui.button(label="Skip", style=disnake.ButtonStyle.green)
    async def skips(self, button, interaction: disnake.Interaction):
        if interaction.guild.voice_client.queue.is_empty:
            return await interaction.response.send_message(
                "Queue is empty, write `>play` to play some music or I will disconnect at the end of the music!",
                ephemeral=True)

        try:
            next_song = interaction.guild.voice_client.queue.get()
            await interaction.guild.voice_client.play(next_song)
            embed = disnake.Embed(title=f"Music from - {interaction.guild.voice_client.track.author} ",
                                  description=f"[{interaction.guild.voice_client.track.title}]({str(interaction.guild.voice_client.track.uri)})",
                                  color=0x2F3136)
            embed.add_field(name="Artist:", value=f"**`{interaction.guild.voice_client.track.author}`**", inline=True)
            embed.add_field(name="Duration:",
                            value=f"**`{str(datetime.timedelta(seconds=interaction.guild.voice_client.track.length))}`**",
                            inline=True)
            embed.set_footer(text=f"Music by Que")
            embed.set_image(url=f"{interaction.guild.voice_client.track.thumbnail}")
            await interaction.edit_original_message(embed=embed, view=queueView())
        except Exception:
            return await interaction.response.send_message(
                "Queue empty, write `>play` to play some music or I will disconnect at the end of the music!",
                ephemeral=True)

    @disnake.ui.button(label="Resume/Pause", style=disnake.ButtonStyle.blurple)
    async def resume_and_pause(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if interaction.guild.voice_client.is_paused():
            await interaction.guild.voice_client.resume()
        else:
            await interaction.guild.voice_client.pause()

    @disnake.ui.button(label="Disconnect", style=disnake.ButtonStyle.danger)
    async def dc(self, button, interaction):
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message(
            embed=disnake.Embed(title="Dissconect", description="I have disconnected", color=0x2F3136))


class Music(commands.Cog):
    """Music commands"""

    def __init__(self, bot: commands.Bot):
        super(Music, self).__init__()
        self.bot = bot

    async def cog_load(self) -> None:
        async def setup_hook(self) -> None:
            sc = spotify.SpotifyClient(
                client_id='35e4a1289f4745f494aa9e6c418c9a0a',
                client_secret='2fe747df85f34bbdb23557e7ce31dc9b'
            )
            node: wavelink.Node = wavelink.Node(uri='http://localhost:2333', password='youshallnotpass')
            await wavelink.NodePool.connect(client=self.bot, nodes=[node], spotify=sc)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.id}> is ready!')

    # @commands.command()
    # async def play(self, ctx: commands.Context, search: wavelink.YouTubeTrack, *, channel: disnake.VoiceChannel | None = None):
    #     """Play a song with the given search query.
    #
    #     If not connected, connect to our voice channel.
    #     """
    #     try:
    #         channel = channel or ctx.author.channel.voice
    #     except AttributeError:
    #         return await ctx.send('No voice channel to connect to. Please either provide one or join one.')
    #
    #         # vc is short for voice client...
    #         # Our "vc" will be our wavelink.Player as type-hinted below...
    #         # wavelink.Player is also a VoiceProtocol...
    #
    #     vc = await channel.connect(cls=wavelink.Player)
    #     await vc.play(search)

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first, lol")
        else:
            vc: wavelink.Player = ctx.author.channel.voice

        tracks = await wavelink.YouTubeTrack.search(str(search))
        track = tracks[0]

        if vc.queue.is_empty and not vc.is_playing():
            await vc.play(search)
            embed = disnake.Embed(title=f"Music from - {track.author} ",
                                  description=f"[{track.title}]({str(track.uri)})", color=0x2F3136)
            embed.add_field(name="Artist:", value=f"**`{track.author}`**", inline=True)
            embed.add_field(name="Duration:", value=f"**`{str(datetime.timedelta(seconds=track.length))}`**",
                            inline=True)
            embed.set_footer(text=f"Music by Que")
            embed.set_image(url=f"{track.thumbnail}")
            await ctx.send(embed=embed, view=queueView())
        else:
            await vc.queue.put_wait(search)
            await ctx.send(
                embed=disnake.Embed(title="Queue", description=f"{search.title} added to the queue!", color=0x2F3136))
        vc.ctx = ctx
        try:
            if vc.queue.loop is True: return
        except (Exception, BaseException, disnake.Forbidden):
            setattr(vc, "loop", False)

    # @commands.Cog.listener()
    # async def on_wavelink_node_ready(self, node: wavelink.Node):
    #     print(f"Node {node.identifier} ready!")
    #
    # async def start_nodes(self):
    #     await self.bot.wait_until_ready()
    #     await wavelink.NodePool.create_node(bot=self.bot, host='lava.link', port=80, password='dismusic',
    #                                         spotify_client=spotify.SpotifyClient(
    #                                             client_id="35e4a1289f4745f494aa9e6c418c9a0a",
    #                                             client_secret="2fe747df85f34bbdb23557e7ce31dc9b"))
    #
    # @commands.command()
    # async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack):
    #     if not ctx.voice_client:
    #         vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    #     elif not getattr(ctx.author.voice, "channel", None):
    #         return await ctx.send("Join a voice channel first, lol")
    #     else:
    #         vc: wavelink.Player = ctx.voice_client
    #
    #     if vc.queue.is_empty and not vc.is_playing():
    #         await vc.play(search)
    #         embed = disnake.Embed(title=f"Music from - {vc.track.author} ",
    #                               description=f"[{vc.track.title}]({str(vc.track.uri)})", color=0x2F3136)
    #         embed.add_field(name="Artist:", value=f"**`{vc.track.author}`**", inline=True)
    #         embed.add_field(name="Duration:", value=f"**`{str(datetime.timedelta(seconds=vc.track.length))}`**",
    #                         inline=True)
    #         embed.set_footer(text=f"Music by Que")
    #         embed.set_image(url=f"{vc.track.thumbnail}")
    #         await ctx.send(embed=embed, view=queueView())
    #     else:
    #         await vc.queue.put_wait(search)
    #         await ctx.send(
    #             embed=disnake.Embed(title="Queue", description=f"{search.title} added to the queue!", color=0x2F3136))
    #     vc.ctx = ctx
    #     try:
    #         if vc.loop: return
    #     except (Exception, BaseException, disnake.Forbidden):
    #         setattr(vc, "loop", False)
    #
    # @commands.command()
    # async def queue(self, ctx):
    #     if not ctx.voice_client:
    #         vc: wavelink.Player = await ctx.channel.connect(cls=wavelink.Player)
    #     elif not getattr(ctx.author.voice, "channel", None):
    #         return await ctx.send("Join the voice channel first.")
    #     else:
    #         vc: wavelink.Player = ctx.voice_client
    #
    #         if not vc.is_playing():
    #             embed = disnake.Embed(title="Music", description="Man, nothing is playing yet ....", color=0x2F3136)
    #             embed.set_footer(text="Man, why can't people be a little smarter?")
    #             await ctx.send(embed=embed)
    #
    #         embed = disnake.Embed(title=f"Music from - {vc.track.author} ",
    #                               description=f"[{vc.track.title}]({str(vc.track.uri)})", color=0x2F3136)
    #         embed.add_field(name="Artist:", value=f"**`{vc.track.author}`**", inline=True)
    #         embed.add_field(name="Duration:", value=f"**`{str(datetime.timedelta(seconds=vc.track.length))}`**",
    #                         inline=True)
    #         embed.set_footer(text=f"Music by Que")
    #         embed.set_image(url=f"{vc.track.thumbnail}")
    #         await ctx.send(embed=embed, view=queueView())
    #
    # @commands.command()
    # async def volume(self, ctx, volume: int):
    #     if not ctx.voice_client:
    #         return await ctx.send(
    #             embed=disnake.Embed(title="I'm not even in the voice channel!", color=disnake.Color.red()))
    #     elif not getattr(ctx.author.voice, "channel", None):
    #         return await ctx.send(embed=disnake.Embed(title="Join the channel first, lol", color=disnake.Color.red()))
    #     else:
    #         vc: wavelink.Player = ctx.voice_client
    #
    #     if volume > 100:
    #         return await ctx.send(embed=disnake.Embed(title="It's to big! .-.", color=disnake.Color.red()))
    #     elif volume < 0:
    #         return await ctx.send(embed=disnake.Embed(title="It's to small! ._.", color=disnake.Color.red()))
    #     await ctx.send(embed=disnake.Embed(title="Success",
    #                                        description=f" <:yes:993171492563079260>    |   I have successfuly set the volume to `{volume}`%",
    #                                        color=0x2F3136))
    #     return await vc.set_volume(volume)
    #
    # @commands.command()
    # async def pause(self, ctx: commands.Context):
    #     if not ctx.voice_client:
    #         return await ctx.send(embed=disnake.Embed(title="<:no:993171433981227058> | I'm not even in vc, lol",
    #                                                   color=disnake.Color.red()))
    #     elif not getattr(ctx.author.voice, "channel", None):
    #         return await ctx.send(
    #             embed=disnake.Embed(title="<:no:993171433981227058> | Join a voice channel first, lol",
    #                                 color=disnake.Color.red()))
    #     else:
    #         vc: wavelink.Player = ctx.voice_client
    #     if not vc.is_playing():
    #         return await ctx.send(embed=disnake.Embed(title="<:no:993171433981227058> | Play some music first, lol",
    #                                                   color=disnake.Color.red()))
    #
    #     await vc.pause()
    #     await ctx.send(embed=disnake.Embed(title="<:yes:993171492563079260> | Music is now paused", color=0x2F3136),
    #                    view=queueView())
    #
    # @commands.command()
    # async def resume(self, ctx: commands.Context):
    #     if not ctx.voice_client:
    #         return await ctx.send(embed=disnake.Embed(title="<:no:993171433981227058> | I'm not even in vc, lol",
    #                                                   color=disnake.Color.red()))
    #     elif not getattr(ctx.author.voice, "channel", None):
    #         return await ctx.send(
    #             embed=disnake.Embed(title="<:no:993171433981227058> | Join a voice channel first, lol",
    #                                 color=disnake.Color.red()))
    #     else:
    #         vc: wavelink.Player = ctx.voice_client
    #     if vc.is_playing():
    #         return await ctx.send(embed=disnake.Embed(title="<:no:993171433981227058> | Music is already playing, lol",
    #                                                   color=disnake.Color.red()))
    #
    #     await vc.resume()
    #     return await ctx.send(
    #         embed=disnake.Embed(title="<:yes:993171492563079260> | Music is now resumed", color=0x2F3136),
    #         view=queueView())
    #
    # @commands.command()
    # async def skip(self, ctx: commands.Context):
    #     if not ctx.voice_client:
    #         return await ctx.send(embed=disnake.Embed(title="<:no:993171433981227058> | I'm not even in vc, lol",
    #                                                   color=disnake.Color.red()))
    #     elif not getattr(ctx.author.voice, "channel", None):
    #         return await ctx.send(
    #             embed=disnake.Embed(title="<:no:993171433981227058> | Join a voice channel first, lol",
    #                                 color=disnake.Color.red()))
    #     else:
    #         vc: wavelink.Player = ctx.voice_client
    #     if not vc.is_playing():
    #         return await ctx.send(embed=disnake.Embed(title="<:no:993171433981227058> | Play some music first, lol",
    #                                                   color=disnake.Color.red()))
    #
    #     try:
    #         next_song = vc.queue.get()
    #         await vc.play(next_song)
    #         embed = disnake.Embed(title=f"Music from - {vc.track.author} ",
    #                               description=f"[{vc.track.title}]({str(vc.track.uri)})", color=0x2F3136)
    #         embed.add_field(name="Artist:", value=f"**`{vc.track.author}`**", inline=True)
    #         embed.add_field(name="Duration:", value=f"**`{str(datetime.timedelta(seconds=vc.track.length))}`**",
    #                         inline=True)
    #         embed.set_footer(text=f"Music by Que")
    #         embed.set_image(url=f"{vc.track.thumbnail}")
    #         await ctx.send(embed=embed, view=queueView())
    #     except (Exception, BaseException, disnake.Forbidden):
    #         return await ctx.send(embed=disnake.Embed(
    #             title="<:no:993171433981227058> | Que is empty. Play some music, or I'll leave when this song ends.",
    #             color=disnake.Color.red()))
    #
    #     await vc.stop()
    #
    # @commands.command()
    # async def disconnect(ctx: commands.Context):
    #     if not ctx.voice_client:
    #         return await ctx.send(embed=disnake.Embed(title="<:no:993171433981227058> | I'm not even in vc, lol",
    #                                                   color=disnake.Color.red()))
    #     elif not getattr(ctx.author.voice, "channel", None):
    #         return await ctx.send(
    #             embed=disnake.Embed(title="<:no:993171433981227058> | Join a voice channel first, lol",
    #                                 color=disnake.Color.red()))
    #     else:
    #         vc: wavelink.Player = ctx.voice_client
    #
    #     await vc.disconnect()
    #     return await ctx.send(
    #         embed=disnake.Embed(title="<:yes:993171492563079260> | I have left teh channel.", color=0x2F3136))
    #
    # @commands.command()
    # async def splay(self, ctx: commands.Context, *, search: str):
    #     if not ctx.voice_client:
    #         vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    #     elif not getattr(ctx.author.voice, "channel", None):
    #         return await ctx.send(embed=disnake.Embed(title="Error",
    #                                                   description="<:no:993171433981227058> | Join a voice channel first, lol 🤣😂",
    #                                                   color=disnake.Color.red()))
    #     else:
    #         vc: wavelink.Player = ctx.voice_client
    #
    #     if vc.queue.is_empty and not vc.is_playing():
    #         try:
    #             track = await spotify.SpotifyTrack.search(query=search, return_first=True)
    #             await vc.play(track)
    #             embed = disnake.Embed(title=f"Music from - {vc.track.author} ",
    #                                   description=f"[{vc.track.title}]({str(vc.track.uri)})", color=0x2F3136)
    #             embed.add_field(name="Artist:", value=f"**`{vc.track.author}`**", inline=True)
    #             embed.add_field(name="Duration:", value=f"**`{str(datetime.timedelta(seconds=vc.track.length))}`**",
    #                             inline=True)
    #             embed.set_footer(text=f"Music by Que")
    #             embed.set_image(url=f"{vc.track.thumbnail}")
    #             await ctx.send(embed=embed, view=queueView())
    #         except Exception as e:
    #             await ctx.send(embed=disnake.Embed(title="Error",
    #                                                description="<:no:993171433981227058> | Please enter a spotify, son **url**",
    #                                                color=disnake.Color.red()))
    #     else:
    #         await vc.queue.put_wait(search)
    #         await ctx.send(embed=disnake.Embed(title="Queue", description=f"Added to the queue!", color=0x2F3136))
    #     vc.ctx = ctx
    #     try:
    #         if vc.loop: return
    #     except Exception:
    #         setattr(vc, "loop", False)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Music(bot))
