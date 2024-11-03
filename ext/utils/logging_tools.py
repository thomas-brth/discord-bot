# Logging custom configs

#############
## Imports ##
#############

import logging
import enum

###############
## Constants ##
###############

SWITCHER = {
	"DEBUG": logging.DEBUG,
	"INFO": logging.INFO,
	"WARNING": logging.WARNING,
	"ERROR": logging.ERROR,
	"CRITICAL": logging.CRITICAL
}

#############
## Classes ##
#############

## Custom filters ##

class LevelFilter():
	"""
	Enable filtering on logging level.
	
	Mode "remove" disables the logger for a specific level.
	Mode "less" disables the logger for all levels under the given level. This mode isn't useful as handlers configuration already does the job.
	Mode "above" disables the logger for all levels above the given level.
	"""
	def __init__(self, level : str, mode : str = "remove"):
		super(LevelFilter, self).__init__()
		self.level = SWITCHER[level]
		self.mode = mode

	def filter(self, record):
		"""
		Called by the logger.

		------------
		Parameters :
			- record : the LogRecord passed by the logger.
		"""
		if self.mode == "remove":
			return self.level != record.levelno
		elif self.mode == "less":
			return self.level <= record.levelno
		elif self.mode == "above":
			return self.level >= record.levelno

## TO DO : other custom filters ##

###############
## Functions ##
###############

def main():
	f = LevelFilter(level=logging.DEBUG, mode="remove")

if __name__ == '__main__':
	main()