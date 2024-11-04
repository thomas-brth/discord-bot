# Discord bot main script 

#############
## Imports ##
#############

## Discord imports ##
import discord
from discord import app_commands
from discord.ext import commands

## Other imports ##
from dotenv import load_dotenv
load_dotenv()
import os
import sys
sys.path.append("ext")
sys.path.append("ext\\utils")
sys.path.append("ext\\resources")
import asyncio

###############
## Constants ##
###############

###########
## Class ##
###########

class MainBot(commands.Bot):
	"""
	Override commands
	Bot to include a test mode and encapsulate async functions.
	"""
	def __init__(self, test_mode : bool, **kwargs):
		super(MainBot, self).__init__(**kwargs)
		self.test_mode = test_mode
		self.token = os.getenv("TEST_BOT") if self.test_mode else os.getenv("BOT")
		
		# Context Menu function model
		@self.tree.context_menu(name="date")
		async def show_joined_date(interaction : discord.Interaction, member : discord.Member):
			await interaction.response.send_message(f"Arrivé sur le serveur le : {member.joined_at}", ephemeral=True)

		# Other context menus ?

	async def execute(self):
		"""
		Start the bot.
		Call both bot.connect() and bot.login() functions, the latter calling the bot.setup_hook() function.
		"""
		await self.start(token=self.token, reconnect=True)

	async def setup_hook(self):
		"""
		A coroutine to be called to setup the bot, by default this is blank.
		This is only called once, inside login() call, and will be called before any events are dispatched, making it a better solution than doing such setup in the on_ready() event.
		"""
		try:
			await self.load_extension("admin") # load the admin extension
		except Exception as e:
			raise e

	## ERROR HANDLER ? ##

###############
## Functions ##
###############

async def main():
	"""
	Main function.
	Async Bot initialisation.
	"""
	desc = """A simple bot, by Atomix."""
	
	intents = discord.Intents.all()
	bot = MainBot(test_mode=True, command_prefix=['!', '.'], description=desc, intents=intents)

	# Delete the command before its execution.
	@bot.before_invoke
	async def delete_message(ctx : commands.Context):
		await ctx.message.delete()
	
	# Start the client
	await bot.execute()

if __name__ == '__main__':
	print(f"Currently using discord python API {discord.__version__}.", flush=True)
	asyncio.run(main())