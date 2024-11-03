# Admin extension

#############
## Imports ##
#############

## Discord imports ##
import discord
from discord.ext import commands
from discord import app_commands

## Other imports ##
from dotenv import load_dotenv
load_dotenv()
import os
import asyncio
import time

## Logging imports ##
import logging
from logging.config import dictConfig
import yaml

###############
## Constants ##
###############

#############
## Classes ##
#############

class Admin(commands.Cog):
	"""
	----------------
	Admin extension.
	----------------

	Gather all the commands to manage the bot, and handle the errors.
	When loaded, a logger is set up.
	"""

	def __init__(self, client : commands.Bot):
		self.client = client
		self.guild_id = os.getenv("TEST_GUILD") if self.client.test_mode else os.getenv("GUILD")
		self.guild = None
		self.personnal_id = int(os.getenv("PERSONAL_ID"))
		self.client.owner_id = self.personnal_id
		self.logger = None

	async def cog_check(self, ctx : commands.Context):
		"""
		Check to be executed before any command.
		"""
		return True

	async def cog_load(self):
		"""
		Called when the cog is loaded.
		Enable asynchronous tasks to be performed outside the __init__() function.
		"""
		# Setup logger
		with open(os.path.join(os.path.dirname(__file__), 'utils/log_config.yaml'), 'r') as stream:
			log_config = yaml.load(stream, Loader=yaml.FullLoader)

		dictConfig(log_config)
		self.logger = logging.getLogger(__name__)
		self.logger.info("Logger ready.")

	############
	## Events ##
	############

	@commands.Cog.listener()
	async def on_ready(self):
		self.logger.info("Client ready.")
		self.guild = discord.utils.get(self.client.guilds, id=int(self.guild_id))
		self.client.get_command('help').cog = self # Set 'help' command as an Admin command

	@commands.Cog.listener()
	async def on_command_error(self, ctx : commands.Context, error : BaseException):
		"""
		An error handler that is called when an error is raised inside a command either through user input error, check failure, or an error in the code.
		"""
		self.logger.error(error)

		try:
			# Check which error is triggered for custom responses
			if issubclass(type(error), commands.UserInputError):
				await ctx.send(f"Tu as mal utilisé la commande {ctx.command.name}.", delete_after=5)
			elif issubclass(type(error), commands.DisabledCommand):
				await ctx.send(f"La commande {ctx.command.name} a été désactivée.", delete_after=5)
			elif issubclass(type(error), commands.CommandNotFound):
				await ctx.send("Impossible de trouver la commande.", delete_after=5)
			elif issubclass(type(error), commands.CheckFailure):
				await ctx.send("Tu n'as pas la permission d'effectuer cette commande.", delete_after=5)
			elif issubclass(type(error), commands.CommandOnCooldown):
				await ctx.send("Cette commande est en cooldown, attends un peu.", delete_after=5)
			elif issubclass(type(error), commands.ExtensionError):
				await ctx.send("Un problème a été rencontré lors du chargement de l'extension.", delete_after=5)
			else:
				await ctx.send("Une erreur est survenue.", delete_after=5)
		except Exception as e:
			self.logger.error(e)
		
	##############
	## Commands ##
	##############

	@commands.command(
		name="quit",
		help="Déconnecte le bot du serveur."
		)
	@commands.is_owner()
	async def quit(self, ctx : commands.Context):
		"""
		Disconnect the cliet from the server.
		"""
		if self.client.voice_clients:
			await ctx.send("Impossible de me déconnecter. Je dois d'abord quitter les salons vocaux.", delete_after=10)
		else:
			self.logger.info("Client disconnected from the server.")
			await self.client.close()

	@commands.command(
		name="purge",
		help="Supprime les messages."
		)
	@commands.is_owner()
	async def purge(self, ctx : commands.Context, n : int = 10):
		"""
		Purge a defined amount of messages.
		"""
		try:
			await ctx.channel.purge(limit=n)
		except Exception as e:
			raise e

	@commands.command(
		name="load",
		help="Ajoute une extension au bot."
		)
	@commands.is_owner()
	async def load(self, ctx : commands.Context, extension : str):
		"""
		Load an extension.
		"""
		try:
			await self.client.load_extension(extension)
			self.logger.info(f"Extension {extension} loaded.")
			await ctx.send(f"L'extension {extension} a été chargée.", delete_after=10)
		except Exception as e:
			raise e

	@commands.command(
		name="unload",
		help="Enlève une extension au bot."
		)
	@commands.is_owner()
	async def unload(self, ctx : commands.Context, extension : str):
		"""
		Unload an extension.
		"""
		try:
			if extension != "admin":
				await self.client.unload_extension(extension)
				self.logger.info(f"Extension {extension} unloaded.")
			else:
				await ctx.send(f"Impossible d'enlever l'extension: {extension}.", delete_after=10)
		except Exception as e:
			raise e

	@commands.command(
		name="reload",
		help="Charge une nouvelle fois toutes les extensions"
		)
	@commands.is_owner()
	async def reload(self, ctx : commands.Context):
		"""
		Reload all extensions.
		"""
		try:
			extensions = list(self.client.extensions)
			for ext in extensions:
				if ext != "admin":
					await self.client.reload_extension(name=ext)
					await ctx.send(f"Extension '{ext}' chargée.", delete_after=10)
		except Exception as e:
			raise e

	@commands.command(
		name="ext",
		help="Liste les extensions actuellement chargées par le bot."
		)
	@commands.is_owner()
	async def list_ext(self, ctx : commands.Context):
		"""
		List all extensions currently loaded.
		"""
		await ctx.send(f"Voici les extensions actuellement utilisées : {', '.join([ext for ext in self.client.extensions])}.", delete_after=15)

	@commands.command(
		name="sync",
		help="Synchronise les commandes avec le bot."
		)
	@commands.is_owner()
	async def sync(self, ctx : commands.Context):
		"""
		Sync Discord bot command tree.
		"""
		synced = await self.client.tree.sync()
		self.logger.info(f"{len(synced)} command(s) synced.")

	####################
	## Slash Commands ##
	####################

	@app_commands.command(
		name="ping",
		description="Pong !"
		)
	async def ping(self, interaction : discord.Interaction):
		"""
		Check bot latency.
		"""
		await interaction.response.send_message(f"Pong !\nLatence : {round(self.client.latency*1000, 0)} ms", ephemeral=True)

####################
## Setup function ##
####################

async def setup(client):
	"""
	Setup the cog.
	"""
	await client.add_cog(Admin(client))