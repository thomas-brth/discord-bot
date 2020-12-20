# Admin extension

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
import time

###############
## Constants ##
###############

TEST_MODE = True
GUILD = os.getenv("TEST_GUILD") if TEST_MODE else os.getenv("GUILD")
PERSONAL_ID = os.getenv("PERSONAL_ID")

#############
## Classes ##
#############

class Admin(commands.Cog):
	"""
	Extension with admin commands.
	"""
	def __init__(self, client : commands.Bot):
		self.client = client
		self.guild = None
		self.personnal_id = int(PERSONAL_ID)
		self.client.owner_id = self.personnal_id

	async def cog_check(self, ctx):
		"""
		Check to be executed before any command.
		"""
		return True

	############
	## Events ##
	############

	@commands.Cog.listener()
	async def on_ready(self):
		self.guild = discord.utils.get(self.client.guilds, id=int(GUILD))
		channel = self.guild.system_channel
		if channel is not None:
			await channel.send("Salut tout le monde!", delete_after=10)
		self.client.get_command('help').cog = self # Set 'help' command as an Admin command
	
	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		"""
		Triggered when an exception is raised.
		"""
		
		#if ctx is not None and ctx.message is not None:
		#	await ctx.message.delete()
		
		ignored = (commands.CommandNotFound, commands.UserInputError)
		error = getattr(error, 'original', error)
		
		if isinstance(error, ignored):
			pass
		elif isinstance(error, commands.BadArgument):
			await ctx.send(f"Tu as entré de mauvais arguments pour la commande {ctx.command.name}.", delete_after=10)
		elif isinstance(error, commands.DisabledCommand):
			await ctx.send(f"La commande {ctx.command.name} a été désactivée.", delete_after=10)
		elif isinstance(error, commands.CheckFailure):
			await ctx.send("Tu n'as pas la permission d'effectuer cette commande.", delete_after=10)
		elif isinstance(error, commands.CommandOnCooldown):
			await ctx.send("Cette commande est en cooldown, attends un peu.", delete_after=10)
		else:
			await ctx.send("Une erreur est survenue.", delete_after=10)

		raise error
		
	##############
	## Commands ##
	##############

	@commands.command(
		name="disconnect",
		brief="Déconnecte le bot.",
		help=f"Déconnecte le bot du serveur."
		)
	@commands.is_owner()
	async def disconnect(self, ctx):
		await ctx.message.delete()
		if self.client.voice_clients:
			await ctx.send("Impossible de me déconnecter. Je dois d'abord quitter les salons vocaux.", delete_after=10)
		else:
			await ctx.send("À la prochaine!", delete_after=5)
			await asyncio.sleep(6)
			await self.client.close()

	@commands.command(
		name="purge",
		help="Supprime les messages."
		)
	@commands.is_owner()
	async def purge(self, ctx, n : int = 10):
		"""
		Purge message up to 'time' s ago.
		"""
		await ctx.message.delete()
		try:
			await ctx.channel.purge(limit=n)
		except Exception as e:
			raise e

	@commands.command(
		name="load",
		help="Ajoute une extension au bot."
		)
	@commands.is_owner()
	async def load(self, ctx, extension : str):
		"""
		Load an extension.
		"""
		await ctx.message.delete()
		try:
			self.client.load_extension(extension)
			await ctx.send(f"L'extension {extension} a été chargée.", delete_after=10)
			await ctx.send("Voici les commandes utilisables:", delete_after=10)
			await ctx.send_help(extension.capitalize())

		except Exception as e:
			raise e
			await ctx.send(f"Impossible de charger l'extension: {extension}\nErreur: {e}", delete_after=10)

	@commands.command(
		name="unload",
		help="Enlève une extension au bot."
		)
	@commands.is_owner()
	async def unload(self, ctx, extension : str):
		"""
		Unload an extension.
		"""
		await ctx.message.delete()
		try:
			if extension != "admin":
				self.client.unload_extension(extension)
			else:
				await ctx.send(f"Impossible d'enlever l'extension: {extension}.", delete_after=10)
		except Exception as e:
			await ctx.send(f"Impossible d'enlever l'extension: {extension}\nErreur: {e}", delete_after=10)
			raise e

	@commands.command(
		name="list",
		help="Liste les extensions disponibles."
		)
	@commands.is_owner()
	async def list_ext(self, ctx):
		"""
		List extensions currently available.
		"""
		await ctx.message.delete()
		l_ext = os.listdir("ext")
		await ctx.send("Voici les extensions disponibles: ", delete_after=30)
		for ext in l_ext:
			if ext != ".env" and os.path.isfile("ext\\"+ext):
				name_ext = ext.split('.')[0]
				await ctx.send(name_ext, delete_after=30)

####################
## Setup function ##
####################

def setup(client):
	"""
	Setup the cog.
	"""
	client.add_cog(Admin(client))