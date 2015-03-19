"""
IRC bot class
Matthew Russell
last updated Mar 5 2015

class handles the bot's functions
maintains list of active servers, default nickname
loads settings from Settings.py
handles and/or passes terminal input
"""
from Server import Server
from Settings import SETTINGS
from Logger import Logger

class Bot():
	def __init__(self):		
		self.servList = {} # list of servers connected to
		self.servKey = None # current server index
		self.nickName = "PyBot"

		self.logger = Logger("BOT_ERRORS")

		self.loadSettings()

	def quit(self, msg = None): # close all servers
		self.saveSettings()

		for servID in self.servList.keys():
			self.servList[servID].stop(msg)


	def loadSettings(self): #load settings from file
		self.nickName = SETTINGS["NAME"]

		# load servers
		for key in SETTINGS["SERVLIST"].keys():
			serv = SETTINGS["SERVLIST"][key]
			# connect to server and add to list
			self.newServer(serv["HOST"], serv["PORT"], key, serv["PASSWORD"], serv["QUITMSG"])

			for line in serv["ONLOGINCMDS"]: # execute listed commands on login
				options = line.split()
				cmd = options.pop(0)
				self.clientCommand(cmd, options)

			# load channels for server
			server = self.getServer()
			for chanKey in SETTINGS["SERVLIST"][key]["CHANLIST"].keys():
				chan = serv["CHANLIST"][chanKey]
				# tell server to connect to channel
				server.newChannel(chan["NAME"], chanKey, chan["PASSWORD"], chan["LOG"], chan["BANNEDMODS"])

	def saveSettings(self):
		#TODO
		pass


	def newServer(self, host, port, ServerID = None, password = None, quitMessage = ""): # connect to a server and set to current
		if ServerID == None:
			ServerID = "%s.%i" % (host, int(port))
		# make new server
		newServ = Server(host, int(port), self.nickName, ServerID, password, quitMessage)
		# connect server to host
		if(not newServ.closed): # if successful
			# add server to list
			self.servList[ServerID] = newServ
			# set to active server
			self.servKey = ServerID
		else:
			return self.logger.error("Could not connect to server at [%s:%i]" % (host, int(port)))

	def swapServer(self, serverID): # swap current server if valid action
		if serverID in self.servList:
			self.servKey = serverID
		else:
			return self.logger.error("Bad server key: [%s]" % (serverID))

	def closeServer(self, serverID = None, msg = None): # close server connection
		if serverID == None: # set to default if ID not given
			serverID = self.servKey
		if serverID in self.servList: # if server exists
			self.servList[serverID].stop(msg) # tell server to close connection
			del self.servList[serverID] # remove server from list

			if(serverID == self.servKey): # if server key is current server, swap to active one
				if(len(self.servList.keys()) == 0): # if there are no connected servers
					self.servKey = None
					return("No other connected servers available")
				else:
					self.servKey = list(self.servList.keys())[0] # get 0-index of server key list
					return("Setting active Server to %s" % (self.servKey))
		else:
			return self.logger.error("Bad server key: [%s]" % (serverID))

	def getServer(self, serverID = None): # return server object, default if not specified
		if(serverID == None): # if no server specified, use default
			serverID = self.servKey
		if(serverID == None): # if server doesn't exist, raise exception
			raise Exception("No connected Servers! Please connect to a server before continuing: /server host port")
		return self.servList[serverID] # return server from list

	def getServerKey(self): # return current server key
		if(self.servKey == None):
			return "None"
		return self.servKey

	# pass forwards :---------------------------------------------

	def clientMessage(self, msg): # pass message to default server & chan
		#
		self.getServer().sendMsg(msg)

	def clientCommand(self, cmd, options): # terminal command input
		if   cmd == "server" or cmd == "s": 
			return self.newServer(*options)
		elif cmd == "setse" or cmd == "ss":
			return self.swapServer(*options)
		elif cmd == "close":
			server = options.pop(0)
			msg = None
			if(len(options) > 0):
				msg = " ".join(options)
			return self.closeServer(server, msg)
		else: # else pass to current server
			return self.getServer().clientCommand(cmd, options)




