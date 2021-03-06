# Tools for music bot

#############
## Imports ##
#############

import youtube_dl as yt
from urllib import parse, request
import re

###############
## Constants ##
###############

YDL_OPT = {
			'format' : 'bestaudio',
			'postprocessors' : [{
				'key' : 'FFmpegExtractAudio',
				'preferredcodec' : 'mp3'
			}],
			'logger' : None,
			'progress_hooks' : []
		}

#############
## Classes ##
#############

class Logger():
	"""
	"""
	def debug(self, msg):
		pass

	def warning(self, msg):
		print(f"WARNING : {msg}", flush=True)

	def error(self, msg):
		print(f"ERROR : {msg}", flush=True)

class Song():
	"""
	Song object, gathering both music metadata and invoking context.
	"""
	def __init__(self, info : dict, ctx):
		self._info = info
		self.ctx = ctx

	@property
	def url(self):
		return self._info['url']

	@property
	def yt_url(self):
		return self._info['webpage_url']

	@property
	def title(self):
		return self._info['title']

	@property
	def id(self):
		return self._info['id']	

	@property
	def views(self):
		return self._info['view_count']

	@property
	def uploader(self):
		return self._info['uploader']

	@property
	def uploader_url(self):
		return self._info['uploader_url']

	@property
	def likes(self):
		return self._info['like_count']

	@property
	def upload_date(self):
		return self._info['upload_date'] #YYYYMMDD

	@property
	def description(self):
		return self._info['description']

	@property
	def duration(self):
		time_in_s = int(self._info['duration'])
		time_in_min = time_in_s//60
		hh = time_in_min//60
		mm = time_in_min%60
		ss = time_in_s%60
		return f"{hh}h{mm}m{ss}s"

	@property
	def duration_in_s(self):
		return int(self._info['duration'])

	@property
	def thumbnail(self):
		return self._info['thumbnail']

	def __str__(self):
		return f"{self.title} - [{self.duration}] - Demandé par {self.ctx.author.name} "
		

###############
## Functions ##
###############

def hook(info):
	"""
	Hook to be called when a download is finished.
	"""
	if info['status'] == 'downloading':
		# Downloading information
		print(f"Elapsed: {round(info['elapsed'], 2)}s - Eta:  {info['eta']}s - Speed: {round(info['speed'] / 1e6, 3)}Mo/s", flush=True)

def yt_extract_info(query):
	"""
	Return info of searched video.
	"""
	query_string = parse.urlencode({'search_query': query})
	htm_content = request.urlopen('http://www.youtube.com/results?'+query_string)
	search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
	res = 'http://www.youtube.com/watch?v='+search_results[0]

	opt = YDL_OPT
	opt['logger'] = Logger()
	opt['progress_hooks'].append(hook)

	with yt.YoutubeDL(opt) as ydl:
		info = ydl.extract_info(res, download=False)

	return info

def yt_extract_info_from_url(url : str):
	"""
	Extract info from a youtube url.
	"""
	opt = YDL_OPT
	opt['logger'] = Logger()
	opt['progress_hooks'].append(hook)

	with yt.YoutubeDL(opt) as ydl:
		info = ydl.extract_info(url, download=False)

	return info

def main():
	pass

if __name__ == '__main__':
	main()