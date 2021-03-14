# Blindtest tools

#############
## Imports ##
#############

import discord
import numpy as np

###############
## Constants ##
###############

SPECIAL_CHAR = {
	'a' : ['à', 'â', 'ã'],
	'e' : ['é', 'è', 'ê', 'ë'],
	'i' : ['î', 'ï'],
	'o' : ['ô', 'õ'],
	'u' : ['ù', 'û', 'ü'],
	'y' : ['ÿ'],
	'c' : ['ç'],
	'n' : ['ñ'],
	' ' : ["'", '$', '*', '%', '^', '@', '#', '/']
}
WRONG_ANSWER = 0
TITLE_ONLY = 1
ARTISTS_ONLY = 2
RIGHT_ANSWER = 3

#############
## Classes ##
#############

###############
## Functions ##
###############

def normalize_string(s : str):
	"""
	Remove accent and change to lower case.
	"""
	for key in SPECIAL_CHAR.keys():
		for char in SPECIAL_CHAR[key]:
			s = s.replace(char, key)
	return s.lower()

def match_ref(answer : str, ref : str):
	"""
	Return True if the ref is contained inside the answer.
	"""
	return ref in answer

def process(message : discord.Message, title : str, artists : list):
	"""
	Evaluate the answer.
	"""
	content = normalize_string(message.content)
	type = WRONG_ANSWER
	max_lenght = len(title+" "+" ".join(artists)) + 1
	if match_ref(answer=content, ref=normalize_string(title)) and len(content) <= max_lenght:
		type = TITLE_ONLY
	if np.array([normalize_string(artist) in content for artist in artists]).all() and len(content) <= max_lenght:
		type = RIGHT_ANSWER if type == TITLE_ONLY else ARTISTS_ONLY
	return type

def main():
	pass

if __name__ == '__main__':
	main()