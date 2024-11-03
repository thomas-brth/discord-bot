# Title

#############
## Imports ##
#############

## Discord imports ##
import discord
from discord.ext import commands
from discord import app_commands

## General imports ##
from dotenv import load_dotenv
load_dotenv()
import os
import enum
import random as rd

###############
## Constants ##
###############

TEST_MODE = False
GUILD = os.getenv("TEST_GUILD") if TEST_MODE else os.getenv("GUILD")
PERSONAL_ID = os.getenv("PERSONAL_ID")

#############
## Classes ##
#############

## Game ##

class CardValue(enum.Enum):
	"""
	Enumeration of all possible card values.
	"""
	TWO = 2
	THREE = 3
	FOUR = 4
	FIVE = 5
	SIX = 6
	SEVEN = 7
	EIGHT = 8
	NINE = 9
	TEN = 10
	JACK = 11
	QUEEN = 12
	KING = 13
	ACE = 14

	def __ge__(self, card_value):
		return self.value >= card_value.value

	def __le__(self, card_value):
		return self.value <= card_value.value

	def __gt__(self, card_value):
		return self.value > card_value.value

	def __lt__(self, card_value):
		return self.value < card_value.value

	def __eq__(self, card_value):
		return self.value == card_value.value

	def __ne__(self, card_value):
		return self.value != card_value.value

	def __str__(self):
		if self.value == 11 or self.value == 12 or self.value == 13 or self.value == 14 :
			return self.name.lower()
		else :
			return str(self.value)

class HandCombinations(enum.Enum):
	"""
	Enumeration of all possible hand combinantions.
	"""
	HIGH_CARD = 1
	PAIR = 2
	TWO_PAIR = 3
	THREE_OF_A_KIND = 4
	STRAIGHT = 5
	FLUSH = 6
	FULL_HOUSE = 7
	FOUR_OF_A_KIND = 8
	STRAIGHT_FLUSH = 9
	ROYAL_FLUSH = 10

	@classmethod
	def check_flush(cls, hand : list):
		"""
		Check if the hand is a flush.

		---------------
		Parameters :
		- hand : list
			A list of five cards.	
		"""
		assert len(hand) == 5
		l_copy = hand.copy()


	@classmethod
	def check_straight(cls, hand : list):
		"""
		Check if the hand is a straight.

		---------------
		Parameters :
		- hand : list
			A list of five cards.	
		"""
		assert len(hand) == 5
		l_copy = hand.copy()
		l_copy.sort()
		for i in range(4):
			if (l_copy[i+1].value - l_copy[i].value) != 1 :
				return False
		return True


class CardSuit(enum.Enum):
	"""
	Enumeration of all possible card suits.
	"""
	CLUBS = 1
	HEARTS = 2
	DIAMONDS = 3
	SPADES = 4

	def __str__(self):
		return self.name.lower()

class Card(tuple):
	"""
	Playing card.
	"""
	def __new__(self, value : CardValue, suit : CardSuit):
		return tuple.__new__(Card, (value, suit))

	def __repr__(self):
		return f"{str(self.value)} of {str(self.suit)}"

	def __ge__(self, other_card):
		return self.value >= other_card.value

	def __le__(self, other_card):
		return self.value <= other_card.value

	def __gt__(self, other_card):
		return self.value > other_card.value

	def __lt__(self, other_card):
		return self.value < other_card.value

	def __eq__(self, other_card):
		return self.value == other_card.value

	def __ne__(self, other_card):
		return self.value != other_card.value

	@property
	def card_value(self):
		return self[0]

	@property
	def suit(self):
		return self[1]

	@property
	def value(self):
		return self.card_value.value

	@property
	def name(self):
		return self.suit.name

	@property
	def image(self):
		return os.path.normpath(os.path.join(os.path.join(os.path.dirname(__file__), os.path.join("resources", os.path.join("images", "cards"))), f"{str(self.value)}_of_{str(self.suit)}.png"))

class Deck():
	"""
	Deck containing 52 cards.
	It is randomly shuffled during initialisation.
	"""
	def __init__(self):
		super(Deck, self).__init__()
		self.cards = [Card(value, suit) for value in CardValue for suit in CardSuit]
		rd.shuffle(self.cards)

	@property
	def remaining(self):
		"""
		Return the number of cards remaining in the deck.
		"""
		return len(self.cards)

	def draw(self):
		"""
		Draw a card, and remove it from the deck.
		"""
		if self.remaining > 0 :
			return self.cards.pop(0)

	def reset(self):
		"""
		Reset the deck.
		"""
		self.__init__()

class Player():
	"""
	"""
	def __init__(self, user : discord.Member):
		super(Player, self).__init__()
		self.user = user
		self.cash = None
		self.hand = None

class PokerGame():
	"""
	"""
	def __init__(self, players : set):
		super(PokerGame, self).__init__()
		self.players = [Player()]
		rd.shuffle(self.players)
		self.pot = 0
		self.board = []
		self.discard = []

	def new_round(self):
		"""
		Start a new round.
		"""
		self.pot = 0
		self.board = []
		self.discard = []


## Views ##

class RegisterView(discord.ui.View):
	"""
	View used to join a game.
	"""

	def __init__(self, ctx : commands.Context):
		super(RegisterView, self).__init__(timeout=None)
		self.ctx = ctx
		self.users = set()

	@discord.ui.button(label="Rejoindre", style=discord.ButtonStyle.green)
	async def join(self, interaction : discord.Interaction, button : discord.ui.Button):
		"""
		Join the created game.

		------------
		Parameters :
		- interaction : discord.Interaction
			The interaction which triggered this function.
		- button : discord.ui.Button
			The button used to trigger this function.
		"""
		if interaction.user not in self.users :
			self.users.add(interaction.user)
			await interaction.response.send_message("Tu as rejoins la partie !", ephemeral=True)
		else :
			await interaction.response.send_message("Tu es déjà dans la partie !", ephemeral=True)


	@discord.ui.button(label="Quitter", style=discord.ButtonStyle.red)
	async def quit(self, interaction : discord.Interaction, button : discord.ui.Button):
		"""
		Quit the created game.

		------------
		Parameters :
		- interaction : discord.Interaction
			The interaction which triggered this function.
		- button : discord.ui.Button
			The button used to trigger this function.
		"""
		if interaction.user in self.users :
			self.users.remove(interaction.user)
			await interaction.response.send_message("Tu as quitté la partie !", ephemeral=True)
		else :
			await interaction.response.send_message("Tu n'es pas dans la partie !", ephemeral=True)

	@discord.ui.button(label="Commencer", style=discord.ButtonStyle.gray)
	async def begin(self, interaction : discord.Interaction, button : discord.ui.Button):
		"""
		Launch the game.

		------------
		Parameters :
		- interaction : discord.Interaction
			The interaction which triggered this function.
		- button : discord.ui.Button
			The button used to trigger this function.
		"""
		self.stop()
		self.clear_items()
		await interaction.response.send_message(
			f"La partie peut commencer !\nVoici la liste des joueurs dans la partie :{', '.join([user.mention for user in self.users])}",
			ephemeral=False,
			delete_after=30
			)

## Cog ##

class Poker(commands.Cog):
	"""
	Poker Discord extension.
	"""
	def __init__(self, client : commands.Bot):
		super(Poker, self).__init__()
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
		"""
		Called when the extension is loaded.
		"""
		pass

	##############
	## Commands ##
	##############

	@commands.command(
		name="start",
		description="Lance une nouvelle partie."
		)
	@commands.is_owner()
	async def start(self, ctx : commands.Context):
		"""
		Start the game.

		------------
		Parameters :
		- ctx : discord.ext.commands.Context
			The context of the invoking message.
		"""
		register_view = RegisterView(ctx=ctx)
		message = await ctx.send("Une nouvelle partie vient de commencer !", view=register_view)
		await register_view.wait()
		await message.delete()

###############
## Functions ##
###############

####################
## Setup function ##
####################

async def setup(client : commands.Bot):
	"""
	Setup the cog.
	Function executed when the extension is loaded by the bot.

	------------
	Parameters :
	- client : commands.Bot
		The discord bot runing this extension.
	"""
	await client.add_cog(Poker(client))

def main():
	d = Deck()
	hand = [d.draw() for i in range(5)]
	print(hand)
	print(HandCombinations.check_straight(hand))

if __name__ == '__main__':
	main()