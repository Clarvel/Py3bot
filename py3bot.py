#!/usr/bin/python3
"""
IRC bot class
Matthew Russell
last updated June 29 2015

class handles the bot's functions
maintains list of active servers, default nickname
loads settings from Settings.py
handles and/or passes terminal input
"""
import sys

from logger import Logger
from IRCerrors import IRCError, IRCBotError
from settings import SERVERS, NICKS
from IRCserverRFC2812 import IRCServerRFC2812
from terminalListener import TerminalListener

class IRCBot():
	def __init__(self):		
		self.servers = {} # list of servers connected to
		self._currentServerKey = None # current server index
		self._nickNames = ["PyBot"]

		self._methods = {
			"s":self.server,
			"ss":self.swapServer,
			"leave":self.closeServer,
			"close":self.closeServer,
			"this":self.getContext,
			"context":self.getContext
		}

		self._terminal = TerminalListener(self._commandParser, self.getContext)
		self._logger = Logger("BOT_ERRORS")

	#-----------------------------------------------------------------------------

	def start(self):
		"""starts the bot, call only once"""
		self._loadSettings()
		self._terminal.start()

	def quit(self, *msg):
		"""
		closes all connected servers
		kills terminal listener
		"""
		self._saveSettings()
		self._terminal.stop()
		for s in self.servers.keys():
			self.servers[s].disconnect(" ".join(msg))

	def _loadSettings(self): #load settings from file
		try:
			self._nickNames = NICKS
		except Exception as e:
			pass

		# load servers
		for key in SERVERS.keys():
			serv = SERVERS[key]
			# connect to server and add to list
			try:
				self.server(serv["HOST"], serv["PORT"], key, 
					serv.get("PASSWORD", None), serv.get("QUITMSG", None))
			except Exception as e:
				#print("server load error: %s" % e)
				raise
			else:
				# load channels for server
				server = self._getServer()
				for cKey in SERVERS[key]["CHANNELS"].keys():
					chan = serv["CHANNELS"][cKey]
					# tell server to connect to channel
					server.join(chan["NAME"], chan["PASSWORD"])

				# execute listed commands on login
				for line in serv["ONLOGINCMDS"]: 
					options = line.split()
					cmd = options.pop(0)
					self._commandParser(cmd, options)


	def _saveSettings(self):
		#TODO
		pass

	#-----------------------------------------------------------------------------

	def server(self, host, port, ServerID = None, password = None, quitMessage = None):
		"""connect to a server and set to current"""
		if not ServerID:
			ServerID = "%s.%i" % (host, int(port))
		newServ = IRCServerRFC2812(host, int(port), 
			self._nickNames[0], ServerID, password)
		if quitMessage:
			newServ.quitMessage = quitMessage
		newServ.connect()
		if(newServ.isConnected()):
			self.servers[ServerID] = newServ
			self._currentServerKey = ServerID
		else:
			raise IRCBotError("Could not connect to server at [%s:%i]" % (host, int(port)))

	def swapServer(self, serverID):
		"""swap current server if valid action"""
		if serverID in self.servers:
			self._currentServerKey = serverID
			return self.getContext()
		else:
			raise IRCBotError("Bad server key: [%s]" % (serverID))

	def closeServer(self, serverID = None, msg = None):
		"""close server connection"""
		if not serverID: # set to default if ID not given
			serverID = self._currentServerKey
		if serverID in self.servers: # if server exists
			self.servers[serverID].disconnect(msg) # tell server to close connection
			del self.servers[serverID] # remove server from list

			if(serverID == self._currentServerKey): # if server key is current server, swap to active one
				if(len(self.servers.keys()) == 0): # if there are no connected servers
					self._currentServerKey = None
					return "No other connected servers available"
				else:
					self._currentServerKey = list(self.servers.keys())[0] # get 0-index of server key list
					return "Setting active Server to %s" % (self._currentServerKey)
		raise IRCBotError("Bad server key: [%s]" % (serverID))

	def _getServer(self, serverID = None):
		"""return server object, default if not specified"""
		if(not serverID): # if no server specified, use default
			serverID = self._currentServerKey
		if(not serverID): # if server doesn't exist, raise exception
			raise IRCBotError("No connected Servers! Please connect to a server before continuing: /server host port")
		return self.servers[serverID] # return server from list

	def listServers(self):
		"""lists connected servers"""
		return list(self.servers.keys())

	def listChannels(self, serverID = None):
		if(not serverID): # if no server specified, use default
			serverID = self._currentServerKey
		if(not serverID): # if server doesn't exist, raise exception
			raise IRCBotError("No connected Servers! Please connect to a server before continuing: /server host port")
		return list(self.servers[serverID].receivers.keys()) # return server from list

#-----------------------------------------------------------------------------

	def getContext(self):
		"""
		returns a string containing the current server abbreviation and the current channel/client
		"""
		try:
			channel = self._getServer().getReceiver().name
		except Exception as e:
			channel = "None"
		return "@[%s %s]" % (self._currentServerKey, channel)

#-----------------------------------------------------------------------------

	def _commandParser(self, command, options): # terminal command input
		response = None
		try:
			response = getattr(self, command)(*options)
		except AttributeError as e:
			if command in self._methods:
				response = self._methods[command](*options)
			else:
				try:
					response = self._getServer().commandParser(command, options)
				except IRCError as e2:
					raise IRCBotError("Command not found! [%s] [%s]" % (e, e2))
		if response: 
			print(response)

#-----------------------------------------------------------------------------

if __name__ == '__main__':
	# system check, verify being run in python3
	if sys.version_info < (3, 4, 0):
		print("This bot must be run in Python3\nUsage: python3 __init__.py")
		exit(1)
	else:
		bot = IRCBot()
		print("Welcome to\n _____       ____  ____        __\n |  __ \     |___ \|  _ \      | |\n | |__) |   _  __) | |_) | ___ | |_\n |  ___/ | | ||__ <|  _ < / _ \| __|\n | |   | |_| |___) | |_) | (_) | |_\n |_|    \__, |____/|____/ \___/ \__|\n         __/ |\n        |___/\nInput commands:")
		bot.start()

