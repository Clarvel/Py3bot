"""
IRC channel class
Matthew Russell
last updated Mar 18, 2015

class stores data and calls mods and logs server messages
"""

from Logger import Logger
from Settings import SETTINGS
from ModLoader import ModLoader

class Channel():
	def __init__(self, name, host, msgCallback, prepend = None, logit = True, bannedMods = None):
		self.name = name # channel name
		self.host = host
		self.msgCallback = msgCallback
		self.cmdChar = SETTINGS["ALERTCHAR"]

		if(logit):
			self.logger = Logger("%s/%s" % (host, name), prepend)

		self.mods = ModLoader(self.name, self.chanCallback)
		modsList = []
		if bannedMods == None:
			modsList = SETTINGS["MODS"]
		else:
			for mod in SETTINGS["MODS"]: # find all mods to load and load them
				if mod not in bannedMods:
					modsList.append(mod)

		print(self.mods.load(modsList))

	def chanCallback(self, message, channel = None): # sets default channel to this, not to server's current channel
		if channel == None:
			channel = self.name
		self.msgCallback(message, channel)

	def msg(self, sender, message): # channel message received
		self.log("%s: %s" % (sender, message))

		if message.startswith(self.cmdChar):
			options = message.split()
			command = options.pop(0)
			self.mods.callMod(sender, command[1:], " ".join(options))
		
	def act(self, sender, action): # channel message is an action
		self.log("*%s %s" % (sender, action))

	def mtn(self, sender, message): # was mentioned in a channel
		self.log("%s: %s" % (sender, message))

		self.mods.mentMod(sender, message)

	def log(self, msg): # log msg to channel
		try:
			self.logger.log(msg)
		except AttributeError as e:
			pass

	def getName(self):
		return self.name

	def clientCommand(self, cmd, options):
		optStr = " ".join(options) # pre-concat options string
		if   cmd == "load":
			return self.mods.load(options)
		elif cmd == "reload":
			return self.mods.load(options)
		elif cmd == "stop":
			return self.mods.stop(optStr)
		elif cmd == "loaded" or cmd == "mods":
			return(self.mods.modsList())
		else:
			raise Exception("Bad command: [%s]" % cmd)

