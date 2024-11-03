# discord-bot
*Simple Discord bot with extensions.*

This bot showcases multiple functionalities through modular extensions, using Discord Python API [discord.py](https://discordpy.readthedocs.io/en/stable/).

## Setup

### Dependancies
Required Python librairies can be found in `requirement.txt` file.

>Some extensions might need more librairies.

### Environment & Discord bots
The very first steps of deploying a Discord bot on your server is to declare one on the Discord website. Check [this tutorial](https://discordpy.readthedocs.io/en/stable/discord.html). Once you're done, you'll be able to retrieve its associated token.

This bot uses environment variables stored in `.env` files. These can be found within the source code and extensions folders.
```
src\
|-- ext\
|   |-- .env (2)
|   |-- admin.py
|-- main.py
|-- .env (1)
```
- The root-level .env file (1) needs to contain the token associated with your Discord bot.
```
# .env
BOT="YOUR TOKEN HERE"
```
- The extension-level .env file (2) can contains various variables, depending on your extensions.

### Launching
Once cloned, this repository is ready to go ! Make sure you have a decent internet connection, and run the `main.py` file.

## Extensions
As of today, the bot has 5 extensions, including the ***Admin*** extension. When starting the bot, the latter is forcibly loaded. It gathers administrator-only commands, and should be used to control the bot general behavior.

List of available extensions :
- **Admin** : Gather all the administrator commands and handle errors. This exention can't be loaded nor unloaded.
- **Blindtest** : *To do*
- **Music** : Music extension for Discord bots. Play music in a voice chanel directly from Youtube. **FFmpeg needed**
- **Poker** : *To do*
- **Quizz** : *To do*

Each extension is a python file with an entry point called `setup`. It adds the cog to the client - here the bot which loads the extension. You can add custom extensions in the `ext\` folder, with the same code structure as shown below :
```python
import Discord
from Discord.ext import commands

class SomeExtension(commands.Cog):
	
	def __init__(self, client : commands.Bot):
		self.client = client
	
	#Add custom asynchronous methods inside this class, e.g. event listeners, commands, properties...

async def setup(client):
	await client.add_cog(SomeExtension(client=client))
```
Any extension can be loaded using the `load` command defined in the Admin extensions. On loading, a check will be performed [to ensure the environment is correctly set up](#Setup).