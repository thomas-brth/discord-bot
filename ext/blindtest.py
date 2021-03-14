# Blintest extension

#############
## Imports ##
#############

## Discord import ##
import discord
from discord.ext import commands

## Other imports ##
import json
import time
import random as rd
from dotenv import load_dotenv
load_dotenv()
import os
import sys
import asyncio

## Custom imports ##
from utils import music_tools, blindtest_tools

###############
## Constants ##
###############

TEST_MODE = True
GUILD = os.getenv("TEST_GUILD") if TEST_MODE else os.getenv("GAMES_GUILD")
PERSONAL_ID = os.getenv("PERSONAL_ID")

#############
## Classes ##
#############

class Blindtest(commands.Cog):
	"""
	Blindtest extension for discord bots.

	Play with friends and try to guess songs' title and author.
	"""
	def __init__(self, client : commands.Bot):
		self.client = client
		self.guild = discord.utils.get(self.client.guilds, id=int(GUILD))
		self.personnal_id = int(PERSONAL_ID)
		self.client.owner_id = self.personnal_id

		self.duration = 30

		self.players = {}
		with open(os.path.join(os.path.dirname(__file__), "resources\\data\\blindtest_musics.json"), 'r', encoding='utf-8') as foo:
			self.data = json.load(foo)
			foo.close()
		self.registered_musics = {}
		
		self.current_music_meta = None
		self.accepting_answers = False
		self.accepting_title_guess = False
		self.accepting_artists_guess = False

		self.voice_channel = None
		self.voice_client = None
		self.default_channel = None

	def add_player(self, member_id : int):
		"""
		Add a player to the game.
		"""
		if member_id not in self.players.keys():
			self.players[member_id] = {"score" : 0, "streak" : 0}
			return True
		else:
			return False


	def end_round(self, e):
		"""
		End current round. Function to be called after a song has finished to be played.
		"""
		if e is not None:
			raise e
		self.accepting_answers = False
		self.accepting_title_guess = False
		self.accepting_artists_guess = False
		embed = discord.Embed(title="Et la bonne réponse était...", color=0xf70006)
		embed.add_field(name=" ".join(self.current_music_meta['artists']), value=self.current_music_meta['title'])
		asyncio.run_coroutine_threadsafe(self.default_channel.send(embed=embed), loop=self.voice_client.loop)

	async def display_categories(self, ctx):
		"""
		Display current selected categories.
		"""
		embed = discord.Embed(title="Catégories sélectionnées :", description=", ".join(self.registered_musics.keys()), color=0xf70006)
		count = 0
		for cat in self.registered_musics.keys():
			count += len(self.registered_musics[cat])
		embed.add_field(name="Nombre de musiques", value=count)
		await ctx.send(embed=embed, delete_after=30)
	
	############
	## Events ##
	############

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.channel == self.default_channel and self.accepting_answers and message.author.id != self.client.user.id and message.author.id in self.players.keys():
			answer_type = blindtest_tools.process(message=message, title=self.current_music_meta['title'], artists=self.current_music_meta['artists'])
			if answer_type == blindtest_tools.RIGHT_ANSWER:
				self.accepting_answers = False
				self.players[message.author.id]['score'] += 3
				if self.current_music_meta['hard']:
					self.players[message.author.id]['score'] += 2
					await message.channel.send(f"Bravo {message.author.mention}! Tu as découvert le titre et le(s) artiste(s)! Tu marques 5 points.")
				else:
					await message.channel.send(f"Bravo {message.author.mention}! Tu as découvert le titre et le(s) artiste(s)! Tu marques 3 points.")
			elif answer_type == blindtest_tools.TITLE_ONLY and self.accepting_title_guess:
				self.accepting_title_guess = False
				self.players[message.author.id]['score'] += 1
				if self.current_music_meta['hard']:
					self.players[message.author.id]['score'] += 1
					await message.channel.send(f"Bravo {message.author.mention}! Tu as découvert le titre! Tu marques 2 point.")
				else:
					await message.channel.send(f"Bravo {message.author.mention}! Tu as découvert le titre! Tu marques 1 point.")
			elif answer_type == blindtest_tools.ARTISTS_ONLY and self.accepting_artists_guess:
				self.accepting_artists_guess = False
				self.players[message.author.id]['score'] += 1
				if self.current_music_meta['hard']:
					self.players[message.author.id]['score'] += 1
					await message.channel.send(f"Bravo {message.author.mention}! Tu as découvert le(s) artiste(s)! Tu marques 2 point.")
				else:
					await message.channel.send(f"Bravo {message.author.mention}! Tu as découvert le(s) artiste(s)! Tu marques 1 point.")
			else:
				# Do nothing
				pass
		else:
			# Do nothing
			pass

	##############
	## Commands ##
	##############

	@commands.command(
		name="start",
		help="Active le mode audio."
		)
	@commands.is_owner()
	async def start(self, ctx, mode : str = "all"):
		"""
		Start audio mode and make the bot join a given voice channel.
		"""
		self.default_channel = discord.utils.get(self.guild.channels, id=ctx.message.channel.id)
		await ctx.message.delete()
		voice = ctx.author.voice
		if voice is None:
			await ctx.send("Connecte toi sur un salon vocal avant d'exécuter cette commande!", delete_after=10)
		else:
			self.voice_channel = voice.channel
			for member_id in self.voice_channel.voice_states:
				_bool = self.add_player(member_id=member_id)
			self.voice_client = await self.voice_channel.connect()
			if mode == "all":
				for cat in self.data['categories']:
					self.registered_musics[category] = self.data[cat]
				await self.display_categories(ctx)
			elif mode == "facile":
				self.registered_musics['facile'] = self.data['facile']

	@commands.command(
		name="join",
		help="Rejoins la partie en cours de jeu.",
		aliases=["j"]
		)
	async def join(self, ctx):
		"""
		"""
		await ctx.message.delete()
		_bool = self.add_player(member_id=ctx.author.id)
		if _bool:
			await ctx.send(f"{ctx.author.mention} a rejoint la partie!", delete_after=10)
		else:
			await ctx.send("Tu es déjà dans la partie!", delete_after=10)

	@commands.command(
		name="new",
		help="Commence une nouvelle partie.",
		aliases=['n']
		)
	@commands.is_owner()
	async def new(self, ctx):
		"""
		Reset game parameters.
		"""
		await ctx.message.delete()

		self.registered_musics = {}
		for player_id in self.players.keys():
			self.players[player_id]['score'] = 0
			self.players[player_id]['streak'] = 0

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

	@commands.command(
		name="add",
		help="Ajoute une catégorie.",
		aliases=['a']
		)
	@commands.is_owner()
	async def add(self, ctx, category : str):
		"""
		Add a category.
		"""
		if ctx is not None:
			await ctx.message.delete()

		if category in self.data['categories'] and category not in self.registered_musics.keys():
			self.registered_musics[category] = self.data[category]
			await self.display_categories(ctx)
		else:
			await ctx.send(f"Impossible d'ajouter cette catégorie.", delete_after=10)

	@commands.command(
		name="remove",
		help="Enlève une catégorie.",
		aliases=['r']
		)
	@commands.is_owner()
	async def remove(self, ctx, category : str):
		"""
		Remove a category.
		"""
		await ctx.message.delete()

		if category in self.registered_musics.keys():
			self.registered_musics.pop(category)
			await self.display_categories(ctx)
		else:
			await ctx.send("Impossible d'enlever cette category.", delete_after=10)

	@commands.command(
		name="show",
		help="Affiche les catégories sélectionnées",
		aliases=['s']
		)
	@commands.is_owner()
	async def show_categories(self, ctx):
		"""
		Send an Embed with categories info.
		"""
		await ctx.message.delete()
		await self.display_categories(ctx)

	@commands.command(
		name="next",
		help="Joue la prochaine musique à deviner."
		)
	@commands.is_owner()
	async def next(self, ctx):
		"""
		Play next song to be guessed.
		"""
		if ctx is not None:
			self.ctx = ctx
			await ctx.message.delete()

		# Choose a random category among selected ones
		categories = list(self.registered_musics.keys())
		cat = None
		while cat is None and len(categories) > 0:
			cat = categories.pop(rd.randrange(len(categories)))
			if len(self.registered_musics[cat]) == 0:
				cat = None

		if cat is not None:
			# select a random music from the selected category
			self.current_music_meta = self.registered_musics[cat].pop(rd.randrange(len(self.registered_musics[cat])))

			yt_info = music_tools.yt_extract_info_from_url(self.current_music_meta['url'])
			self.current_music_meta['song'] = music_tools.Song(yt_info, ctx)

			options = {
				'before_options': f"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {self.current_music_meta['start_time']} -t {self.duration}",
				'options': "-vn"
			}
		
			source = discord.FFmpegPCMAudio(self.current_music_meta['song'].url, **options)
			source = discord.PCMVolumeTransformer(source, volume=1.0)
			self.accepting_answers = True
			self.accepting_title_guess = True
			self.accepting_artists_guess = True
			self.voice_client.play(source, after=self.end_round)
		else:
			await ctx.send(f"Il n'y a plus de musiques à faire deviner.", delete_after=10)

	@commands.command(
		name="volume",
		help="Change le volume du bot (entre 0 et 100)."
		)
	@commands.is_owner()
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

	@commands.command(
		name="score",
		help="Affiche les scores de chaque joueur."
		)
	@commands.is_owner()
	async def score(self, ctx):
		"""
		Display each player's score.
		"""
		await ctx.message.delete()

		for player_id in self.players.keys():
			member = await self.guild.fetch_member(player_id)
			await ctx.send(f"{member.mention} : {self.players[player_id]['score']}")

###############
## Functions ##
###############

def setup(client):
	"""
	Setup the Cog
	"""
	client.add_cog(Blindtest(client))