"""
IRC bot class
Matthew Russell
last updated Feb 28 2015

class handles the bot's functions
maintains list of active servers, default nickname, and command alert char
loads settings from Settings.py
handles and/or passes terminal input
"""
from Server import Server
from Settings import SETTINGS
from Logger import Logger
#import ModLoader

class Bot():
	def __init__(self):		
		self.servList = {} # list of servers connected to
		self.servKey = None # current server index
		self.nickName = "PyBot"
		self.alertChar = '!'

		self.logger = Logger("BOT_ERRORS")
		#self.modLoader = ModLoader()

		self.loadSettings()

	def quit(self, msg = ""): # close all servers
		for servID in self.servList.keys():
			self.servList[servID].close(msg)

	def loadSettings(self):
		#load settings from file
		self.nickName = SETTINGS["NAME"]
		self.mods = SETTINGS["MODS"]
		self.alertChar = SETTINGS["ALERTCHAR"]

		# load servers
		for key in SETTINGS["SERVLIST"].keys():
			serv = SETTINGS["SERVLIST"][key]
			# connect to server and add to list
			self.server(serv["HOST"], serv["PORT"], key, serv["PASSWORD"])
			# set to current server
			self.servKey = key

			# load channels for server
			"""
			for chanKey in SETTINGS["SERVLIST"][key]["CHANLIST"].keys():
				chan = serv["CHANLIST"][chanKey]
				# tell server to connect to channel
				self.servList[self.servKey].channel(chan["NAME"], chanKey, chan["PASSWORD"])
				self.servList[self.servKey].chanKey = chanKey
				"""

	def saveSettings(self):
		#TODO
		pass

	def server(self, host, port, ref_ID, password = None): # connect to a server and set to current
		# make new server
		newServer = Server(self, self.nickName)
		# connect server to host
		connected = newServer.connect(host, int(port), password)
		if(connected):
			# add server to list
			self.servList[ref_ID] = newServer
			# set to active server
			self.servKey = ref_ID
		else:
			self.logger.error("Could not connect to server at [%s:%i]" % (host, int(port)))

	def swapServ(self, servID): # swap current server if valid action
		if servID in self.servList:
			self.servKey = servID
		else:
			self.logger.error("Bad server key: [%s]" % (servID))

	def closeServ(self, servID = None, msg = None): # close server connection
		if servID == None:
			servID = self.servKey
		if servID in self.servList:
			self.servList[servID].close(msg) # tell server to close connection
			del self.servList[servID] # remove server from list

			if(servID == self.servKey): # if server key is current server, swap to active one
				if(len(self.servList.keys()) == 0): # if there are no connected servers
					self.servKey = None
					print("No other connected servers available")
				else:
					self.servKey = list(self.servList.keys())[0]
					print("Setting active Server to %s" % (self.servKey))
		else:
			self.logger.error("Bad server key: [%s]" % (servID))

	def getServ(self): # return current server
		if(self.servKey == None):
			raise Exception("No connected Servers")
		return self.servList[self.servKey]

	def botMsg(self, cmd, args): # call mods through this?
		#TODO with modloader
		pass

	# pass forwards :---------------------------------------------

	def termMsg(self, msg): # check for bot message, else pass message to default server & chan
		if(msg.startswith(self.alertChar)): # if message is a bot command
			options = msg.split() # split at whitespace
			cmd = options.pop(0) # split off command
			cmd = cmd.split(self.alertChar, 1)[1] # remove bot cmd char
			self.botMsg(cmd, options)
		else:
			self.getServ().sendMsg(msg)

	def termCmd(self, cmd, options): # terminal command input
		if   cmd == "server" or cmd == "s": 
			self.server(*options)
		elif cmd == "setse" or cmd == "ss":
			self.swapServ(*options)
		elif cmd == "close":
			self.closeServ(*options)
		else: # else pass to current server
			self.getServ().termCmd(cmd, options)




