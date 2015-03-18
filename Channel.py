"""
IRC channel class
Matthew Russell
last updated Mar 18, 2015

class stores data and calls mods and logs server messages
"""

from Logger import Logger
from Settings import SETTINGS

class Channel():
	def __init__(self, name, host, channelPrepend = None, bannedMods = []):
		self.name = name # channel name
		self.host = host
		self.bannedMods = bannedMods

		self.logger = Logger("%s/%s" % (host, name), channelPrepend)

	def msg(self, msg): # channel message received
		#TODO send to mods
		self.log(msg)
		
	def log(self, msg): # log msg to channel
		self.logger.log(msg)

	def getName(self):
		return self.name