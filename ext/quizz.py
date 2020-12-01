# Quizz extension

#############
## Imports ##
#############

## Discord imports ##
import discord
from discord.ext import commands

## Other imports ##
import requests
import time
from dotenv import load_dotenv
load_dotenv()
import os
import asyncio

###############
## Constants ##
###############

API_KEY = os.getenv('API_KEY')
PERSONAL_ID = os.getenv("PERSONAL_ID")
URL_REQ = "https://www.openquizzdb.org/api.php"
CATEGORIES = [
			  'adultes', 'animaux', 'archeologie', 'arts',
			  'bd', 
			  'celebrites', 'cinema', 'culture',
			  'gastronomie', 'geographie', 
			  'histoire',
			  'informatique', 'internet',
			  'litterature', 'loisirs',
			  'monde', 'musique',
			  'nature',
			  'quotidien',
			  'sciences', 'sports',
			  'television', 'tourisme'
			  ]

#############
## Classes ##
#############

class Quizz(commands.Cog):
	"""
	Quizz extension.
	"""
	def __init__(self, client : commands.Bot):
		self.client = client

		self.personnal_id = int(PERSONAL_ID)
		self.client.owner_id = self.personnal_id

		self.settings = {'difficulty' : 2, 'nb_choices' : 4, 'wiki' : 1}
		self.start_message = None

		self.players = {} # {id : {'name' : name, 'score' : score, 'serie' : serie}}
		self.last_invoked = None
		self.last_question = None

	async def cog_check(self, ctx):
		"""
		Check to be executed before any command.
		"""
		return True

	############
	## Events ##
	############

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		"""
		Event listener for reactions. 
		"""
		if self.start_message is not None and reaction.message == self.start_message:
			## Add players to the game
			if not user.id in self.players.keys():
				_dict = {'name' : user.name, 'score': 0, 'serie' : 0, 'done': False}
				self.players[user.id] = _dict
		elif self.last_question is not None and reaction.message == self.last_question:
			## Check answer
			l_react = ['one', 'two', 'three', 'four']
			if not self.players[user.id]['done'] and reaction.emoji.name in l_react:
				pass
			else:
				pass
				
	##############
	## Commands ##
	##############

	@commands.command(
		name="new_quizz",
		help="Crée une nouvelle partie."
		)
	@commands.is_owner()
	async def new_quizz(self, ctx, nb_choices : int, difficulty : int, wiki : int):
		"""
		Create a new quizz with given parameters.
		"""
		await ctx.message.delete()

		embed = discord.Embed(title="", color=0xf70006)
		embed.set_author(name=ctx.author.name)
		# embed.set_thumbnail()
		desc = ""
		embed.add_field(name="**Description**", value=desc, inline=False)
		rules=""
		embed.add_field(name="**Règles**", value=rules)
		self.start_message = await ctx.send(embed=embed)
		asyncio.sleep(120)
		await self.start_message.delete()
		self.start_message = None

	@commands.command(
		name="next_round",
		help="Passe à la question suivante."
		)
	@commands.is_owner()
	async def next_question(self, ctx):
		"""
		Retrieve and send a new question.
		"""
		await ctx.message.delete()
		print("do nothing", flush=True)

###############
## Functions ##
###############

def format_url(nb_choices : int, category : str = None, difficulty : int = None, wiki : bool = False):
	"""
	Return formated url.
	"""
	key = int(API_KEY)
	formated_url = URL+f"?key={key}&choice={nb_choices}"
	if  category is not None:
		formated_url += "&categ={category}"
	if  difficulty is not None:
		formated_url += "&diff={difficulty}"
	if  wiki:
		formated_url += "&wiki=1"
	return formated_url

def retrieve_question(nb_choices : int, category : str = None, difficulty : int = None, wiki : bool = False):
	"""
	Retrieve a question from the API.
	"""
	url = format_url(nb_choices=nb_choices, category=category, difficulty=difficulty, wiki=wiki)
	try:
		req = requests.get(url)
		data = req.json()
		return data
	except Exception as e:
		raise e

def check_question(data : dict):
	"""
	Return True if the data retrieved are complete.
	"""
	return data['response_code'] == 0


def setup(client):
	"""
	Setup the Cog.
	"""
	client.add_cog(Quizz(client))