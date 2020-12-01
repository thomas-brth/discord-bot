# Music extension

#############
## Imports ##
#############

## Discord imports ##
import discord
from discord.ext import commands

## Other imports ##
from dotenv import load_dotenv
load_dotenv()
import os
import asyncio

## Custom Imports ##
from utils import music_tools

###############
## Constants ##
###############

PERSONAL_ID = os.getenv("PERSONAL_ID")
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

#############
## Classes ##
#############

class Music(commands.Cog):
	"""
	Music extension for discord bots.

	Play music in a vocal channel.
	"""
	def __init__(self, client : commands.Bot):
		self.client = client
		self.personnal_id = int(PERSONAL_ID)
		self.client.owner_id = self.personnal_id
		
		self.voice_channel = None
		self.voice_client = None

		self.playlist = []
		self.current_song = None
		self.last_song_embed = None

	async def cog_check(self, ctx):
		"""
		Check to be executed before any command.
		"""
		return True

	############
	## Events ##
	############
		
	##############
	## Commands ##
	##############
	
	@commands.command(
		name="start",
		help="Active le mode audio."
		)
	@commands.is_owner()
	async def start(self, ctx):
		"""
		Start audio mode and make the bot join a given voice channel.
		"""
		await ctx.message.delete()
		voice = ctx.author.voice
		if voice is None:
			await ctx.send("Connecte toi sur un salon vocal avant d'exécuter cette commande!", delete_after=10)
		else:
			self.voice_channel = voice.channel
			self.voice_client = await self.voice_channel.connect()

	@commands.command(
		name="leave",
		help="Quitte le mode audio."
		)
	@commands.is_owner()
	async def leave(self, ctx):
		"""
		Leave audio channel
		"""
		await ctx.message.delete()
		if self.voice_channel is None or self.voice_client.is_playing():
			await ctx.send("Impossible de se déconnecter à un salon vocal.", delete_after=10)
		else:
			await self.voice_client.disconnect()
			await ctx.send(f"Déconnecté du canal {self.voice_channel}", delete_after=10)
			self.voice_channel = None
			self.voice_client = None
			self.playlist = []
			if self.last_song_embed is not None:
				await self.last_song_embed.delete()
			self.last_song_embed = None

	@commands.command(
		name="move_to",
		help="Change le bot de salon vocal",
		aliases=["move"]
		)
	@commands.is_owner()
	async def move_to(self, ctx, channel : str):
		"""
		Move bot to a different voice channel.
		"""
		await ctx.message.delete()
		new_voice_channel = discord.utils.get(self.guild.voice_channels, channel)
		if new_voice_channel is None:
			await ctx.send("Impossible de trouver le salon demandé.", delete_after=10)
		else:
			if self.voice_client.is_playing():
				self.voice_client.pause()
			self.voice_channel = new_voice_channel
			self.voice_client.move_to(self.voice_channel)
			if self.voice_client.is_paused():
				self.voice_client.resume()


	@commands.command(
		name="play",
		help="Cherche une musique sur Youtube et la joue."
		)
	@commands.cooldown(rate=5, per=30.0)
	async def play(self, ctx, *, query):
		"""
		Play next musique in the playlist.
		"""
		if ctx is not None:
			await ctx.message.delete()
		
		if query:
			info = music_tools.yt_extract_info(query)
			song = music_tools.Song(info, ctx)
		else:
			song = self.playlist.pop(0)

		if self.voice_client.is_playing():
			self.playlist.append(song)
		else:
			# Delete previous embed
			if self.last_song_embed is not None:
				await self.last_song_embed.delete()
			# Create and send an Embed
			embed = discord.Embed(title=song.title, url=song.yt_url, color=0xf70006)
			embed.set_author(name=song.uploader, url=song.uploader_url)
			embed.set_thumbnail(url=song.thumbnail)
			embed.add_field(name="Vues", value=song.views, inline=True)
			embed.add_field(name="Durée", value=song.duration, inline=True)
			self.last_song_embed = await song.ctx.send(embed=embed)

			self.current_song = song
			
			# Play music
			after_func = lambda ctx : self.play_next(ctx)
			source = discord.FFmpegPCMAudio(song.url, **FFMPEG_OPTIONS)
			source = discord.PCMVolumeTransformer(source, volume=1.0) # Transform source to enable volume control
			self.voice_client.play(source, after=after_func)

	def play_next(self, ctx):
		"""
		PLay next music in the playlist.
		"""
		if self.playlist:
			asyncio.run_coroutine_threadsafe(self.play(ctx, query=[]), loop=self.voice_client.loop)
		else:
			# Do nothing
			pass

	@commands.command(
		name="next",
		help="Joue la prochaine musique."
		)
	@commands.cooldown(rate=1, per=15.0)
	async def next(self, ctx):
		"""
		Jump to the next music in the playlist.
		"""
		await ctx.message.delete()
		if not self.playlist:
			await ctx.send("Playlist vide! Utilise la commande **!play** pour ajouter des musiques à la playlist.", delete_after=10)
		else:
			self.voice_client.stop()

	@commands.command(
		name="stop",
		help="Coupe la musique."
		)
	@commands.is_owner()
	async def stop(self, ctx):
		"""
		Stop the player if the music is currently playing.
		"""
		await ctx.message.delete()
		if self.voice_client is not None and self.voice_client.is_playing():
			self.playlist = []
			self.current_song = None
			if self.last_song_embed is not None:
				await self.last_song_embed.delete()
			self.last_song_embed = None
			self.voice_client.stop()
		else:
			await ctx.send("Il n'y a pas de musique actuellement en cours d'écoute.", delete_after=10)

	@commands.command(
		name="pause",
		help="Met la musique en pause."
		)
	@commands.cooldown(rate=2, per=30.0)
	async def pause(self, ctx):
		"""
		Pause the player if the music is currently playing.
		"""
		await ctx.message.delete()
		if self.voice_client is not None and self.voice_client.is_playing():
			self.voice_client.pause()
		else:
			await ctx.send("Il n'y a pas de musique actuellement en cours d'écoute.", delete_after=10)

	@commands.command(
		name="resume",
		help="Remet la musique."
		)
	@commands.cooldown(rate=2, per=30.0)
	async def resume(self, ctx):
		"""
		Resume the player if the music is currently paused.
		"""
		await ctx.message.delete()
		if self.voice_client is not None and self.voice_client.is_paused():
			self.voice_client.resume()
		else:
			await ctx.send("Il n'y a pas de musique actuellement en pause.", delete_after=10)

	@commands.command(
		name="playlist",
		help="Affiche la playlist actuelle."
		)
	@commands.cooldown(rate=5, per=30.0)
	async def display_playlist(self, ctx):
		"""
		Display current playslist.
		"""
		await ctx.message.delete()
		if self.playlist:
			total_time = 0
			await ctx.send("Musiques à venir:", delete_after=10)
			for song in self.playlist:
				await ctx.send(f"{song}", delete_after=10)
				total_time += song.duration_in_s
			total_time_in_min = total_time//60
			hh = total_time_in_min//60
			mm = total_time_in_min%60
			ss = total_time%60
			await ctx.send(f"Durée de la playlist: {hh}h{mm}m{ss}s", delete_after=10)
		else:
			await ctx.send("Aucune musique dans la playlist.", delete_after=10)

	@commands.command(
		name="volume",
		help="Change le volume du bot (entre 0 et 100)."
		)
	@commands.cooldown(rate=1, per=10.0)
	async def volume(self, ctx, volume : int):
		"""
		Change volume of a bot while playing.
		"""
		await ctx.message.delete()
		if self.voice_client is not None and self.voice_client.is_playing():
			if volume > 100 or volume < 0:
				await ctx.send("Tu dois spécifier un niveau de volume entre 0 et 100.", delete_after=10)
			else:
				self.voice_client.source.volume = volume/100
				await ctx.send(f"Volume fixé à {self.voice_client.source.volume*100}%.", delete_after=10)
		else:
			await ctx.send("Il n'y a pas de musique actuellement en cours d'écoute.", delete_after=10)
		

###############
## Functions ##
###############

def setup(client):
	"""
	Setup the Cog.
	"""
	client.add_cog(Music(client))