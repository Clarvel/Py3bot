
from Server import Server
from Settings import SETTINGS
from Logger import Logger
#import ModLoader

class Bot():
	"""
	__init__()
	loadSettings(path)						loads stored settings
	saveSettings()							saves settings
	server(host, port, refID, (password))	makes new server
	activeServ(servID)						swaps current server
	closeServ(servID)						closes server
	nickList								array of nicknames for the bot to choose from
	"""
	def __init__(self):		
		self.servList = {} # list of servers connected to
		self.servKey = None # current server index
		#self.modLoader = ModLoader()
		self.logger = Logger("TEST")
		self.nickName = "PyBot"
		self.alertChar = '!'

		self.loadSettings()

		# setup terminal input loop
		self.loop = True
		while(self.loop):
			a = input("")
			self.termParser(a)

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
			for chanKey in SETTINGS["SERVLIST"][key]["CHANLIST"].keys():
				chan = serv["CHANLIST"][chanKey]
				# tell server to connect to channel
				self.servList[self.servKey].channel(chan["NAME"], chanKey, chan["PASSWORD"])
				self.servList[self.servKey].chanKey = chanKey


	def server(self, host, port, ref_ID, password = None): # connect to a server and set to current
		# make new server
		newServer = Server(self.logger, self.nickName)
		# connect server to host
		newServer.connect(host, int(port), password)

		# add server to list
		self.servList[ref_ID] = newServer
		# set to active server
		self.servKey = ref_ID

	def swapServ(self, servID): # swap current server if valid action
		if servID in self.servList:
			self.servKey = servID
		else:
			self.logger.err("Bad server key: %s" % (servID))

	def closeServ(self, servID): # close server connection
		if servID in self.servList:
			self.servList[servID].close() # tell server to close connection
			del self.servList[servID] # remove server from list

			if(servID == self.servKey):
				self.servKey = self.servList.keys()[0]
				print("Setting active Server to %s" % (self.servKey))
		else:
			self.logger.error("Bad server key: %s" % (servID))

	def termParser(self, msg): # parses terminal input
		options = msg.split()
		cmd = options.pop(0)

		if(cmd.startswith('/')): 	# matches a terminal command
			cmd = cmd.split('/', 1)[1] # remove terminal command id
			if  (cmd == "server"):		# join new server
				self.server(*options)
				return
			elif(cmd == "sset"):		# set current server
				self.swapServ(*options)
				return
			elif(cmd == "quit"):		# leave server
				self.closeServ(*options)
				return
			elif(cmd == "join"):		# join channel
				self.servList[self.servKey].channel(*options)
				return
			elif(cmd == "cset"):		# set current channel
				self.servList[self.servKey].swapChan(*options)
				return
			elif(cmd == "exit"):		# close current channel
				self.servList[self.servKey].closeChan(*options)
				return
			elif(cmd == "pm"):			# send pm
				person = options.pop(0)
				msg = " ".join(options)
				self.servList[self.servKey].sendPM(msg, person)
				return
		elif(cmd.startswith(self.alertChar)): 	# matches a bot command
			cmd = cmd.split(self.alertChar, 1)[1]
			return
		# else send data to server
		self.servList[self.servKey].sendMsg(msg)



"""
	def channel(self, chanName, chanID, password = None): # switch to channel in server or connect to channel in current server
		return self.servList[self.servKey].channel(chanName, chanID, password)

	def swapChan(self, chanID): # swap current channel if valid action
		return self.servList[self.servKey].swapChan(chanID)

	def closeChan(self, chanID): # close server connection
		return self.servList[self.servKey].closeChan(chanID)

	def msg(self, message):
		return self.servList[self.servKey].msg(message)
"""

		