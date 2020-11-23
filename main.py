# Discord bot main script 

#############
## Imports ##
#############

## Discord imports ##
import discord
print(f"Currently using discord python API {discord.__version__}.", flush=True)
from discord.ext import commands

## Other imports ##
from dotenv import load_dotenv
load_dotenv()
import os
import sys
sys.path.append("ext")
sys.path.append("ext\\utils")

###############
## Constants ##
###############

TEST_MODE = True
TOKEN = os.getenv("TEST_BOT") if TEST_MODE else os.getenv("BOT")

###############
## Functions ##
###############

def load(bot : commands.Bot, extension_name : str):
	"""
	load a given extension.
	"""
	try:
		bot.load_extension(extension_name)
	except Exception as e:
		raise e
		print(f"{extension_name} could not be loaded.")

def unload(bot : commands.Bot, extension_name : str):
	"""
	Unload a given extension.
	"""
	try:
		bot.unload_extension(extension_name)
	except Exception as e:
		raise e
		print(f"{extension_name} could not be unloaded.")

def main():
	"""
	Main function. Bot initialisation.
	"""
	desc = """A simple bot, by Atomix."""
	extensions = ["ext.admin"]
	
	bot = commands.Bot(command_prefix=['!', '.'], description=desc)

	# Load main extensions
	for extension in extensions:
		load(bot, extension)

	# Run the client
	bot.run(TOKEN)

if __name__ == '__main__':
	main()