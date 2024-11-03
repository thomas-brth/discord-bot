# Quizz extension

#############
## Imports ##
#############

## Discord imports ##
import discord
from discord.ext import commands
from discord.ext.commands import BucketType as bt

## Other imports ##
import requests
import time
import random as rd
from dotenv import load_dotenv
load_dotenv()
import os
import asyncio
import json

###############
## Constants ##
###############

TEST_MODE = True
GUILD = os.getenv("TEST_GUILD") if TEST_MODE else os.getenv("GAMES_GUILD")
API_KEY = os.getenv('API_KEY')
PERSONAL_ID = os.getenv("PERSONAL_ID")
URL_REQ = "https://www.openquizzdb.org/api.php"

#############
## Classes ##
#############

class Quizz(commands.Cog):
	"""
	Quizz extension.
	"""
	def __init__(self, client : commands.Bot):
		self.client = client
		self.guild = discord.utils.get(self.client.guilds, id=int(GUILD))

		self.personnal_id = int(PERSONAL_ID)
		self.client.owner_id = self.personnal_id

		self.settings = {'timer' : 30, 'nb_choices' : 4, 'difficulty' : 2, 'wiki' : True, 'anec': True}
		self.formated_url = format_url(nb_choices=4, difficulty=2, wiki=True, anec=True)
		with open(os.path.join(os.path.dirname(__file__), "resources\\images\\urls.json"), 'r') as foo:
			self.images_urls = json.load(foo) 
			foo.close()

		self.start_message = None

		self.players = {} # {id : {'name' : name, 'score' : score, 'serie' : serie}}
		self.question_data = None
		self.question = None
		self.answers = {}

	def add_player(self, member):
		"""
		Add a player to the current list.
		"""
		if not member.id in self.players.keys():
			self.players[member.id] = {'name' : member.name, 'score' : 0, 'serie' : 0, 'answer' : None}
			return True
		else:
			return False

	def remove_player(self, member):
		"""
		Remove a player from the current list.
		"""
		if member.id in self.players.keys():
			self.players.pop(member.id)
			return True
		else:
			return False

	def generate_url(self):
		"""
		Generate formated url.
		"""
		self.formated_url = format_url(
			nb_choices=self.settings['nb_choices'],
			difficulty=self.settings['difficulty'],
			wiki=self.settings['wiki'],
			anec=self.settings['anec']
			)


	def check_answer(self, reaction):
		"""
		Check player's answer.
		"""
		return reaction is not None and self.answers[reaction] == self.question_data['results'][0]['reponse_correcte']

	async def cog_check(self, ctx):
		"""
		Check to be executed before any command.
		"""
		return True

	async def send_question(self, ctx):
		"""
		Send question on current channel.
		"""
		l_react = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
		l_answers = self.question_data['results'][0]['autres_choix']
		rd.shuffle(l_answers)
		
		embed = discord.Embed(title="Question", description=self.question_data['results'][0]['question'], color=0xf70006)
		embed.set_thumbnail(url=self.images_urls['question']['url'])

		for i in range(self.settings['nb_choices']):
			self.answers[l_react[i]] = l_answers[i]
			embed.add_field(name=f"{i+1})", value=l_answers[i], inline=False)

		self.question = await ctx.send(embed=embed)
		for r in l_react:
			await self.question.add_reaction(r)

	async def compute_scores(self, ctx):
		"""
		Compute scores of the latest question.
		"""
		for player_id in self.players.keys():
			if self.check_answer(self.players[player_id]['answer']):
				self.players[player_id]['serie'] += 1
				if self.players[player_id]['serie'] < 3:
					score = 1
				elif self.players[player_id]['serie'] < 5:
					score = 2
				else:
					await ctx.send(f"{self.players[player_id]['name']} est sur une série de {self.players[player_id]['serie']} bonnes réponses!", delete_after=10)
					score = 3
				self.players[player_id]['score'] += score
			else:
				self.players[player_id]['serie'] = 0
			self.players[player_id]['answer'] = None

	async def send_answer(self, ctx):
		"""
		Display answer.
		"""
		embed = discord.Embed(title="**Et la bonne réponse était...**", description=self.question_data['results'][0]['reponse_correcte'], color=0xf70006)
		embed.add_field(name="Wiki", value=self.question_data['results'][0]['wikipedia'], inline=False)
		embed.add_field(name="Anecdote", value=self.question_data['results'][0]['anecdote'], inline=False)
		await ctx.send(embed=embed)

	############
	## Events ##
	############

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		"""
		Event listener for reactions. 
		"""
		l_react = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
		if user.id == self.client.user.id:
			return # Do nothing
		elif self.question is not None and reaction.message == self.question and user.id in self.players.keys() and reaction.emoji in l_react:
			self.players[user.id]['answer'] = reaction.emoji
				
	##############
	## Commands ##
	##############

	@commands.command(
		name="timer",
		help="Fixe le temps de réponse pour les questions."
		)
	@commands.is_owner()
	async def set_timer(self, ctx, timer : int):
		"""
		Set time to answer questions.
		"""
		await ctx.message.delete()
		if timer > 5:
			self.settings['timer'] = timer
			await ctx.send(f"Temps de réponse fixé à {timer}s.", delete_after=10)
		else:
			await ctx.send("Le temps de réponse doit être supérieur à 5s.", delete_after=10)

	@commands.command(
		name="diff",
		help="Change les paramètres de la partie."
		)
	@commands.is_owner()
	async def set_difficulty(self, ctx, value : int):
		"""
		Change current difficulty and generate a new url.
		"""
		await ctx.message.delete()
		self.settings['difficulty'] = value
		self.generate_url()
		await ctx.send(f"Difficulté fixée à {value}.", delete_after=10)


	@commands.command(
		name="new_quizz",
		help="Crée une nouvelle partie.",
		aliases=["quizz"]
		)
	@commands.is_owner()
	async def new_quizz(self, ctx):
		"""
		Create a new quizz with given parameters.
		"""
		await ctx.message.delete()
		if self.start_message is not None:
			await self.start_message.delete()

		embed = discord.Embed(title="Nouveau Quizz", color=0xf70006)
		embed.set_author(name=ctx.author.name)
		embed.set_thumbnail(url=self.images_urls['logo']['url'])
		
		
		desc = "Quizz de culture général avec des thèmes très variés. Le vainqueur ne gagne rien, si ce n'est la satisfaction \
		d'être le moins bête."
		embed.add_field(name="**Description**", value=desc, inline=False)
		
		rules="Pour rejoindre la partie, utilise la commande '!join'. Tu peux rejoindre à tout moment.\n\
		À chaque tour, une question est posée avec plusieurs choix possibles. Réagis avec l'emoji :one:, :two:, :three: ou :four: \
		pour donner ta réponse.\n\n**Attention, seule ta dernière réponse est prise en compte.**"
		embed.add_field(name="**Règles**", value=rules, inline=False)
		
		self.start_message = await ctx.send(embed=embed)

	@commands.command(
		name="join",
		help="Rejoins la partie"
		)
	@commands.cooldown(rate=1, per=60, type=bt.user)
	async def join(self, ctx):
		"""
		Join current game.
		"""
		await ctx.message.delete()
		if not self.add_player(ctx.author):
			await ctx.send("Tu es déjà dans la partie.", delete_after=10)
		else:
			await ctx.send(f"{ctx.author.mention} a rejoins la partie.", delete_after=10)
			
	@commands.command(
		name="players",
		help="Affiche les joueurs dans la partie."
		)
	@commands.is_owner()
	async def get_players(self, ctx):
		"""
		Display current players.
		"""
		await ctx.message.delete()
		await ctx.send("Joueurs dans la partie:", delete_after=10)
		for id in self.players.keys():
			await ctx.send(f"{self.players[id]['name']}", delete_after=10)

	@commands.command(
		name="quit",
		help="Quitte la partie."
		)
	@commands.cooldown(rate=1, per=60, type=bt.user)
	async def quit(self, ctx):
		"""
		Quit the current game.
		"""
		await ctx.message.delete()
		if not self.remove_player(ctx.author):
			await ctx.send("Tu n'es pas dans la partie.", delete_after=10)
		else:
			await ctx.send(f"{ctx.author.mention} a quitté la partie.", delete_after=10)

	@commands.command(
		name="question",
		help="Passe à la question suivante."
		)
	@commands.is_owner()
	@commands.cooldown(rate=1, per=60.0)
	async def question(self, ctx):
		"""
		Retrieve and send a new question.
		"""
		await ctx.message.delete()

		if len(self.players.keys()) >= 1:
			self.question_data = retrieve_question(url=self.formated_url)
		
			await self.send_question(ctx)

			time.sleep(self.settings['timer'] - 5)
			await ctx.send("Il ne reste plus que 5 secondes", delete_after=10)
			time.sleep(5)
			await ctx.send("Temps écoulé!", delete_after=10)
			await self.compute_scores(ctx)
			await self.send_answer(ctx)
		else:
			await ctx.send("Il n'y a pas assez de joueurs.", delete_after=10)

	@commands.command(
		name="leaderboard",
		help="Passe à la question suivante.",
		aliases=["lb"]
		)
	@commands.is_owner()
	async def leaderboard(self, ctx):
		"""
		Display current leaderboard.
		"""
		await ctx.message.delete()

		if len(self.players.keys()) >= 1:
			ordered_dict = dict(sorted(self.players.items(), key=lambda item: item[1]['score']))
			embed = discord.Embed(title="**Classement**", color=0xf70006)
			text = ""
			i = 1
			for id in ordered_dict.keys():
				player = ordered_dict[id]
				text += f"{i} - {player['name']} - {player['score']} - {player['serie']}\n"
				i += 1
			embed.add_field(name="Place - joueur - score - série", value=text, inline=False)
			await ctx.send(embed=embed, delete_after=30)
		else:
			await ctx.send("Il n'y a pas assez de joueurs.", delete_after=10)

	@commands.command(
		name="score",
		help="Affiche ton score"
		)
	@commands.cooldown(rate=1, per=60, type=bt.user)
	async def score(self, ctx):
		"""
		Display score of associated player.
		"""
		await ctx.message.delete()

		if ctx.author.id in self.players.keys():
			await ctx.send(f"{ctx.author.name} possède actuellement {self.players[ctx.author.id]['score']} points et est sur une série de {self.players[ctx.author.id]['serie']} bonnes réponses.", delete_after=15)
		else:
			await ctx.send("Tu n'es pas dans la partie.", delete_after=10)

	@commands.command(
		name="end",
		help="Met fin à la partie."
		)
	@commands.is_owner()
	async def end(self, ctx):
		"""
		"""
		await ctx.message.delete()

		if len(self.players.keys()) >= 1:
			ordered_dict = dict(sorted(self.players.items(), key=lambda item: item[1]['score']))
			embed = discord.Embed(title="**Classement final**", color=0xf70006)
			text = ""
			i = 1
			for id in ordered_dict.keys():
				player = ordered_dict[id]
				text += f"{i} - {player['name']} - {player['score']} - {player['serie']}\n"
				i += 1
			embed.add_field(name="Place - joueur - score - série", value=text, inline=False)
			await ctx.send(embed=embed, delete_after=30)
			await ctx.send(f"{self.players[ordered_dict.keys()[0]]['name']} remporte la partie!", delete_after=30)
			self.players = {}
		else:
			await ctx.send("Il n'y a pas assez de joueurs.", delete_after=10)

###############
## Functions ##
###############

def format_url(nb_choices : int = 4, difficulty : int = None, wiki : bool = False, anec : bool = False):
	"""
	Return formated url.
	"""
	key = API_KEY
	formated_url = URL_REQ + f"?key={key}&choice={nb_choices}"
	if  difficulty is not None:
		formated_url += f"&diff={difficulty}"
	if  wiki:
		formated_url += "&wiki=1"
	if anec:
		formated_url += "&anec=1"
	return formated_url

def retrieve_question(url : str):
	"""
	Retrieve a question from the API.
	"""
	try:
		req = requests.get(url)
		data = req.json()
		assert(check_question(data))
		return data
	except Exception as e:
		raise e

def check_question(data : dict):
	"""
	Return True if the data retrieved are complete.
	"""
	return data['response_code'] == 0

####################
## Setup function ##
####################

async def setup(client):
	"""
	Setup the Cog.
	"""
	await client.add_cog(Quizz(client))