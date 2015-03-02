"""
IRC server class
Matthew Russell
last updated Mar 2, 2015

class handles communication between the IRC bot and the connected server

"""



import socket
import threading
import Regexes
import time
from Logger import Logger

class Server():
	"""
	__init__(logger)
	connect(host, port, nickList, (password))	connects to specified server
	channel(name, chanID, (password))			connects to a channel
	close((leaveMessage))						closes connection to server
	swapChan(chanID)							swaps current channel
	closeChan(chanID)							closes channel
	sendMsg(channel, msg)						sends message to a channel
	sendPM(receiver, msg)						sends pm
	nick(name)									sends nick rename message
	performAction(string)						performs action on string input
	"""
	def __init__(self, bot, nickName):
		self.bot = bot
		self.name = nickName
		self.chanList = {}
		self.chanKey = None
		self.closed = True

		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.logger = Logger("")

	def connect(self, host, port, ID, password = None): # connect to server
		if(not self.closed):
			self.logger.error("Server already connected")
			return False

		serv_addr = (host, port)
		self.ID = ID
		self.logger = Logger("servers/%s/%s" % (host, host))
		try:
			self.connection.connect(serv_addr)
		except Exception as e:
			self.logger.error("Connection to host %s failed: %s" % (host, str(e)))
			return False
		else:
			self.closed = False
			self.host = host
			self.logger.info('Connected to %s:%d' % (serv_addr))

			if password != None:
				self.sendData("PASS %s" % (password))

			self.sendData("USER %s %s * :%s" % (self.name, socket.gethostname(), self.name))
			self.sendData("NICK %s" % (self.name))

			self.listenThread = threading.Thread(target=self.listen) # spawn listening thread
			self.listenThread.daemon = True # ensure thread dies when main thread dies
			self.listenThread.start() # start listening thread

			# wait for ping before continuing, otherwise timeout and fail
			self.pinged = False
			timer = 0
			while not self.pinged:
				time.sleep(1)
				timer += 1
				if timer >= 30:
					self.logger.error("Connection to host %s failed: Did not receive ping after %is" % (host, timer))
					return False
			return True

	def close(self, message = ""):
		#closes with optional message
		self.sendData("QUIT %s" % (message))
		self.closed = True


	def channel(self, name, chanID = None, password = ""):
		if(chanID == None):
			chanID = name
		#joins channel
		self.sendData("JOIN %s %s" % (name, password))
		self.chanKey = chanID
		self.chanList[chanID] = name

	def swapChan(self, chanID):
		if chanID in self.chanList.keys():
			self.chanKey = chanID
			print("Setting active Channel to %s" % (self.chanKey))
		else:
			self.logger.error("Bad channel key: %s" % (chanID))

	def closeChan(self, chanID = None):
		# leaves channel
		if chanID == None:
			chanID = self.chanKey
		if chanID in self.chanList.keys():
			self.sendData("PART %s" % (self.chanList[chanID]))
			del self.chanList[chanID]

			if(chanID == self.chanKey):
				if(len(self.chanList.keys()) == 0):
					self.chanKey = None
					print("No other connected channels available")
				else:
					self.chanKey = list(self.chanList.keys())[0]
					print("Setting active Channel to %s" % (self.chanKey))
		else:
			self.logger.error("Bad channel key: %s" % (chanID))

	def getChan(self): # return current channel string
		if(self.chanKey == None):
			raise Exception("No connected Channels for this Server")
		return self.chanList[self.chanKey]

	def getChanKey(self): # return current channel key
		if(self.chanKey == None):
			return "None"
		return self.chanKey

	def listen(self):
		while not self.closed: # while connection isn't closed
			try:
				chunk = self.connection.recv(4096).decode('UTF-8').rstrip() # receive input
			except Exception as e:
				self.logger.error("Connection to host failed: %s" % (str(e)))
				self.closed = True
				return
			else:
				#self.logger.log("[RESP] %s" % chunk)
				if(chunk == ""): # if no data received, bad connection, stop listening
					self.logger.error("No data received, closing connection")
					self.closed = True
				else:
					# otherwise spawn off thread to handle message
					parseThread = threading.Thread(target=self.parseInput, args=(chunk,))
					parseThread.daemon = True
					parseThread.start()

	def parseInput(self, chunk): # Perform some action based on the command fed to the bot
		#print(chunk)
		strList = chunk.split("\n")
		for string in strList:
			string = string.rstrip() # remove unwanted junk from end
			msg = Regexes.REMatch(string)
			if   msg.match(Regexes.PING):
				self.pinged = True
				self.sendData("PONG %s" % (msg.group(1).strip()))
			elif msg.match(Regexes.PMSG):
				if   msg.group(5).startswith(self.bot.alertChar): # bot alert command
					options = msg.group(5).split() # split at whitespace
					cmd = options.pop(0) # split off command
					cmd = cmd.split(self.bot.alertChar, 1)[1] # remove bot cmd char
					self.bot.botMsg(self.ID, self.getChanKey(), msg.group(1), cmd, options)
				else:
					args = Regexes.REMatch(msg.group(5))
					if   args.match(Regexes.ACTN):
						self.logger.log("[%s %s]* %s %s" % (self.ID, msg.group(4), msg.group(1), args.group(1)))
					else:
						self.logger.log("[%s %s %s] %s" % (self.ID, msg.group(4), msg.group(1), msg.group(5)))
			elif msg.match(Regexes.SMSG):
				args = Regexes.REMatch(msg.group(1))
				if   args.match(Regexes.SJON):
					self.logger.info("[SERV_JOIN] %s" % msg.group(2))
				elif args.match(Regexes.SPRM):
					args2 = Regexes.REMatch(args.group(2))
					if   args2.match(Regexes.SMAT):
						self.logger.info("[CHANNAMES] %s" % msg.group(2))
					elif args2.match(Regexes.SMCH):
						self.logger.info("[CHANNEL %s] %s" % (args2.group(1), msg.group(2)))
					else:
						self.logger.info("[SERV_PM] [%s] %s" % (msg.group(1), msg.group(2)))
				else:
					self.logger.info("[SERV_MSG] %s" % ( msg.group(2)))
			elif msg.match(Regexes.NTCE):
				self.logger.log("[NOTICE][%s] %s" % (msg.group(1), msg.group(2)))
			elif msg.match(Regexes.MODE):
				self.logger.info("Mode: %s" % (msg.group(3)))
			elif msg.match(Regexes.JOIN):
				self.logger.info("%s joined channel %s on %s" % (msg.group(1), msg.group(3), self.ID))
			elif msg.match(Regexes.QUIT):
				self.logger.info("[QUIT %s] %s" % (self.ID, msg.group(3)))
			else:
				self.logger.info("[###]%s" % string)

	def sendData(self, msg):
		#Send msg over the connection socket to server
		try:
			#print(msg)
			sent = self.connection.send(bytes("%s\r\n" % (msg), 'UTF-8'))
			if sent == 0:
				raise RuntimeError("Socket Connection Broken")
		except Exception as e:
			self.logger.error("Could not send data: %s" % e)

	def sendMsg(self, msg, channel = None): # send message to channel specified or to current channel otherwise
		if(channel == None): # default to current channel if no chan specified
			channel = self.getChan() # get channel value
		# send data to channel
		self.sendData("PRIVMSG %s :%s" % (channel, msg))

	def sendPM(self, msg, receiver = None): # send message to person specified, or to server otherwise
		# send data to person
		if(receiver == None):
			self.sendData(msg)
		else:
			self.sendData("PRIVMSG %s :%s" % (receiver, msg))

	def nick(self, name):
		# set nickname for bot
		self.sendData(":%s NICK %s" % (self.name, name))
		self.name = name

	def termCmd(self, cmd, options):
		if   cmd == "join" or cmd =="c" or cmd == "channel":
			self.channel(*options)
		elif cmd == "setch"	or cmd == "sc":
			self.swapChan(*options)
		elif cmd == "part":
			self.closeChan(*options)
		else:
			# send message to current server
			optStr = " ".join(options) # preconcat message

			if   cmd == "pm":
				self.sendData("PRIVMSG %s" % (optStr))
			elif cmd == "notice" or cmd == "n":
				self.sendData("NOTICE %s" % (optStr))
			elif cmd == "reply" or cmd == "r":
				pass # TODO
				self.sendData("%s" % (optStr))
			elif cmd == "me":
				self.sendMsg("\x01" + "ACTION %s\x01" % (optStr))
			elif cmd == "oper": 
				self.sendData("OPER %s" % optStr)
			elif cmd == "mode":
				self.sendData("MODE %s %s" % (self.getChan(), optStr))
			elif cmd == "topic" or cmd == "t":
				if(len(options) == 0):
					self.sendData("TOPIC %s" % (self.getChan()))
				else:
					self.sendData("TOPIC %s :%s" % (self.getChan(), optStr))
			elif cmd == "names":
				self.sendData("NAMES %s" % (self.getChan()))
			elif cmd == "nick":
				if(len(options) == 0):
					print("Nickname: [%s]" % self.name)
				else:
					self.nick(optStr)
			elif cmd == "list":
				self.sendData("LIST")
			elif cmd == "invite" or cmd == "inv" or cmd == "i":
				if(len(options) > 1):
					self.sendData("INVITE %s" % (optStr)) # assume channel specified
				else:
					self.sendData("INVITE %s %s" % (optStr, self.getChan()))
			elif cmd == "kick" or cmd == "k":
				self.sendData("KICK %s %s :%s" % (self.getChan(), options.pop(0), " ".join(options)))
			elif cmd == "whois":
				self.sendData("WHOIS %s" % (optStr))
			elif cmd == "whowas":
				self.sendData("WHOWAS %s" % (optStr))
			elif cmd == "kill":
				self.sendData("KILL %s" % (optStr))
			else:
				raise Exception("Bad command: [%s]" % cmd)
