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
	'' : ["'", '$', '*', '%', '^', '@', '#', '/']
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

def hamming_distance(s1 : str, s2 :str):
	"""
	Return the Hamming distance between 2 strings.
	"""
	if len(s1) != len(s2):
		raise ValueError("Lengths mismatch.")
	else:
		dist = 0
		for i in range(len(s1)):
			if s1[i] != s2[i]:
				dist += 1
		return dist

def levenshtein_distance(s1 : str, s2 : str):
	"""
	Return the Levenshtein distance between 2 strings.
	"""
	if min(len(s1), len(s2)) == 0:
		return max(len(s1), len(s2))
	elif s1[0] == s2[0]:
		return levenshtein_distance(s1[1:], s2[1:])
	else:
		return 1 + min(levenshtein_distance(s1[1:], s2), levenshtein_distance(s1, s2[1:]), levenshtein_distance(s1[1:], s2[1:]))

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

def process_enhanced(message : discord.Message, title : str, artists : list, tolerance : int = 2):
	"""
	Evaluate the answer using Levensthein distance.
	"""
	content = normalize_string(message.content)
	type = WRONG_ANSWER
	l_words = content.split(" ")
	possible_answers = [" ".join(l_words[i:i+j+1]) for i in range(len(l_words)) for j in range(len(l_words)-i)]
	count_artists = 0
	for answer in possible_answers:
		if abs(len(answer) - len(title)) <= tolerance - 1:
			if levenshtein_distance(answer, title) <= tolerance:
				type = TITLE_ONLY
		for artist in artists:
			if abs(len(answer) - len(artist)) <= tolerance - 1:
				if levenshtein_distance(answer, artist) <= tolerance:
					count_artists += 1
	if count_artists == len(artists):
		type = RIGHT_ANSWER if type == TITLE_ONLY else ARTISTS_ONLY
	return type
	

def main():
	message = "Flo Rida Good Feeling"
	print(levenshtein_distance("Taoi Cruz", "Taio Cruz"))

if __name__ == '__main__':
	main()