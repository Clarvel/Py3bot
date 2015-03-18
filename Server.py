"""
IRC server class
Matthew Russell
last updated Mar 18, 2015

class handles communication between the IRC bot and the connected server

"""



import socket
import threading
import Regexes
import time
from Logger import Logger
from Channel import Channel

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
	def __init__(self, host, port, nickName = None, serverPrepend = "", password = None, quitMessage = ""):
		self.host = host
		self.name = nickName
		self.servPre = serverPrepend
		self.quitMsg = quitMessage
		self.chanList = {}
		self.chanKey = None
		self.chanIDList = {}
		self.pmIDList = {}
		self.closed = True

		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.logger = Logger("%s/%s" % (host, host), serverPrepend)

		try:
			self.connection.connect((host, port))
		except Exception as e:
			self.logger.error("Connection to host %s failed: %s" % (host, str(e)))
		else:
			self.logger.info('Connecting to %s:%d' % (host, port))

			if password != None:
				self.sendData("PASS %s" % (password))

			self.sendData("USER %s %s * :%s" % (self.name, socket.gethostname(), self.name))
			self.sendData("NICK %s" % (self.name))

			listenThread = threading.Thread(target=self.listen) # spawn listening thread
			listenThread.daemon = True # ensure thread dies when main thread dies
			listenThread.start() # start listening thread

			# wait for ping before continuing, otherwise timeout and fail
			self.pinged = False
			timer = 0
			while not self.pinged:
				time.sleep(1)
				timer += 1
				if timer >= 30:
					self.logger.error("Connection to host %s failed: Did not receive ping after %is" % (host, timer))
					return
			self.closed = False

	def stop(self, message = None):
		#closes with optional message
		if message == None:
			message = self.quitMsg
		for channel in self.chanList.keys(): # log quit messages
			self.chanList[channel].logger.info("QUIT %s" % (message))
		for pmKey in self.pmIDList.keys(): # log quit messages
			self.pmIDList[pmKey].logger.info("QUIT %s" % (message))
		self.logger.log("QUIT %s" % (message))
		self.sendData("QUIT %s" % (message))
		self.closed = True


	def newChannel(self, name, channelID = None, password = "", bannedMods = None):
		if(channelID == None):
			channelID = name

		# make new channel class
		newChan = Channel(name, self.host, "%s %s" % (self.servPre, channelID), bannedMods)

		#commands to join channel
		self.sendData("JOIN %s %s" % (name, password))
		self.chanKey = channelID
		self.chanList[channelID] = newChan
		self.chanIDList[name] = newChan

	def swapChannel(self, channelID):
		if channelID in self.chanList.keys():
			self.chanKey = channelID
			print("Setting active Channel to %s" % (self.chanKey))
		else:
			self.logger.error("Bad channel key: %s" % (channelID))

	def closeChannel(self, channelID = None, msg = None):
		# leaves channel
		if channelID == None:
			channelID = self.chanKey
		if channelID in self.chanList.keys():
			if(msg != None):
				self.sendData("PART %s %s" % (self.chanList[channelID].getName(), msg))
			else:
				self.sendData("PART %s" % (self.chanList[channelID].getName()))				
			del self.chanIDList[self.chanList[channelID].getName()]
			del self.chanList[channelID]

			if(channelID == self.chanKey):
				if(len(self.chanList.keys()) == 0):
					self.chanKey = None
					print("No other connected channels available")
				else:
					self.chanKey = list(self.chanList.keys())[0]
					print("Setting active Channel to %s" % (self.chanKey))
		else:
			self.logger.error("Bad channel key: %s" % (channelID))

	def getChannel(self, channelID = None): # return channel object by its ID or default
		if(channelID == None):
			channelID = self.chanKey
		if(channelID == None):
			raise Exception("No connected Channels for this Server")
		return self.chanList[channelID]

	
	def getPrivateName(self, name): # return channel object by its channel name or find PM
		try:
			private = self.chanIDList[name] # check channels for the channel
		except Exception as e:#channel not found, make new PM as nw channel
			print("[_PM_] %s" % e) # else make new PM, I shouldnt be receiving extraneous channel PMs
			tmp = Channel(name, self.host, "%s %s" % (self.servPre, name), None)
			self.chanIDList[name] = tmp
			private = tmp
		return private

	def getChannelKey(self): # return current channel key
		if(self.chanKey == None):
			return "None"
		return self.chanKey


	def listen(self): # listen to connection, spawn thread to handle message once input received
		self.closed = False
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
		strList = chunk.split("\n") # separate by line
		for string in strList:
			string = string.rstrip() # remove unwanted junk from end of string
			#print(string)
			msg = Regexes.REMatch(string)
			if   msg.match(Regexes.PING): # string matched ping
				self.pinged = True
				self.sendData("PONG %s" % (msg.group(1)))
			elif msg.match(Regexes.USER): # string matched user message
				smsg = Regexes.REMatch(msg.group(4))
				if   smsg.match(Regexes.PMSG): # submessage matched private message
					ssmsg = Regexes.REMatch(smsg.group(2))
					if ssmsg.match(Regexes.ACTN): # subsubmessage matched action
						chan = self.getPrivateName(smsg.group(1)) # find appropriate channel
						chan.msg("*%s %s" % (msg.group(1), ssmsg.group(1)))
					else: # it's a private/channel message
						if(smsg.group(1) != self.name): # if target is not me
							chan = self.getPrivateName(smsg.group(1)) # find appropriate channel
						else:
							chan = self.getPrivateName(msg.group(1))
						chan.msg("%s: %s" % (msg.group(1), smsg.group(2)))
				elif smsg.match(Regexes.JOIN):
					chan = self.getPrivateName(smsg.group(1)) # find appropriate channel
					chan.msg("%s joined %s" % (msg.group(1), smsg.group(1)))
				elif smsg.match(Regexes.NICK):
					self.logger.info("%s is now known as %s" % (msg.group(1), smsg.group(1)))
					#TODO for all channels and pms containing this nick, change their values
				elif smsg.match(Regexes.QUIT):
					self.logger.info("%s quit: %s" % (msg.group(1), smsg.group(1)))
					# TODO propagate this thru all relevant channels
				elif smsg.match(Regexes.PART):
					chan = self.getPrivateName(smsg.group(1))
					chan.msg("%s left: %s" % (msg.group(1), smsg.group(2)))
				elif smsg.match(Regexes.MODE):
					chan = self.getPrivateName(smsg.group(1))
					chan.msg("%s set mode %s %s" % (msg.group(1), smsg.group(2), smsg.group(3)))
				elif smsg.match(Regexes.NTCE):
					chan = self.getPrivateName(smsg.group(1))
					chan.msg("Notice from %s: %s" % (msg.group(1), smsg.group(2)))
				else:
					print("[ ERR ][UNKNOWN USER STRING]%s" % string)
			elif msg.match(Regexes.SERV): # string matched server message
				smsg = Regexes.REMatch(msg.group(4))
				if   smsg.match(Regexes.SNTC): # server authentication notices
					self.logger.info("NOTICE AUTH %s" % (smsg.group(1)))
					#
				elif smsg.match(Regexes.SMOD): # server mode set
					self.logger.info("MODE %s" % (smsg.group(1)))
					#
				elif smsg.match(Regexes.NREP): # string matched numeric reply
					#self.logger.info("[%s] %s" % (smsg.group(1), smsg.group(2)))
					self.numReply(int(smsg.group(1)), smsg.group(2))
				else:
					print("[ ERR ][UNKNOWN SERVER STRING]" % string)
			else:
				print("[ ERR ][UNKNOWN STRING]%s" % string)


	def sendData(self, msg):
		#Send msg over the connection socket to server
		try:
			#print(msg)
			sent = self.connection.send(bytes("%s\r\n" % (msg), 'UTF-8'))
			if sent == 0:
				raise RuntimeError("Socket Connection Broken")
		except Exception as e:
			self.logger.error("Could not send data: %s" % e)

	def sendMsg(self, msg, receiver = None): # send message to channel specified or to current channel otherwise
		if(receiver == None): # default to current channel if no chan specified
			receiver = self.getChannel().getName() # get channel value
		# send data to channel
		self.getPrivateName(receiver).log("%s: %s" % (self.name, msg)) # log message through channel class
		self.sendData("PRIVMSG %s %s" % (receiver, msg))

	def nick(self, name): # change given nickname
		# set nickname for bot
		self.sendData(":%s NICK %s" % (self.name, name))
		self.name = name


	def clientCommand(self, cmd, options): # command received from client
		if   cmd == "join" or cmd =="c" or cmd == "channel":
			self.newChannel(*options)
		elif cmd == "setch"	or cmd == "sc":
			self.swapChannel(*options)
		elif cmd == "part":
			channel = options.pop(0)
			msg = None
			if(len(options) > 0):
				msg = " ".join(options)
			self.closeChannel(channel, msg)
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
				self.sendData("MODE %s %s" % (self.getChannel(), optStr))
			elif cmd == "topic" or cmd == "t":
				if(len(options) == 0):
					self.sendData("TOPIC %s" % (self.getChannel()))
				else:
					self.sendData("TOPIC %s :%s" % (self.getChannel(), optStr))
			elif cmd == "names":
				self.sendData("NAMES %s" % (self.getChannel()))
			elif cmd == "nick":
				if(len(options) == 0):
					print("Nickname: [%s]" % self.name)
				else:
					self.nick(optStr)
			elif cmd == "invite" or cmd == "inv" or cmd == "i":
				if(len(options) > 1):
					self.sendData("INVITE %s" % (optStr)) # assume channel specified
				else:
					self.sendData("INVITE %s %s" % (optStr, self.getChannel()))
			elif cmd == "kick" or cmd == "k":
				self.sendData("KICK %s %s :%s" % (self.getChannel(), options.pop(0), " ".join(options)))
			elif cmd == "whois":
				self.sendData("WHOIS %s" % (optStr))
			elif cmd == "whowas":
				self.sendData("WHOWAS %s" % (optStr))
			elif cmd == "kill":
				self.sendData("KILL %s" % (optStr))
			else:
				raise Exception("Bad command: [%s]" % cmd)

	def numReply(self, num, reply): # numeric replies
		msg = Regexes.REMatch(reply)
		if num <= 0:
			raise Exception("ERROR: Bad Numeric Reply [%i]" % num)
		elif num < 4 or num == 251 or num == 255 or num == 375 or num == 372 or num == 376: # server messages
			msg.match(Regexes.SMSG) # match to general server message
			self.logger.log(msg.group(1))
		elif num == 252:
			msg.match(Regexes.OMSG) # match to operator server message
			self.logger.log("%s %s" % (msg.group(1), msg.group(2)))
		elif num == 254:
			msg.match(Regexes.CMSG) # match to channels server message
			self.logger.log("%s %s" % (msg.group(1), msg.group(2)))
		elif num == 265:
			msg.match(Regexes.LMSG) # match to local users server message
			self.logger.log(msg.group(3))
		elif num == 266:
			msg.match(Regexes.GMSG) # match to global users server message
			self.logger.log(msg.group(3))
		elif num == 353:
			msg.match(Regexes.NAMS) # match to names list
			self.getPrivateName(msg.group(2)).log("USERS: %s" % msg.group(3))
		elif num == 366: #end of names list
			#msg.match(Regexes.ENNL)
			pass
		elif num == 332: # topic
			msg.match(Regexes.TMSG)
			self.getPrivateName(msg.group(1)).log("USERS: %s" % msg.group(2))
		elif num == 333: # creator
			#msg.match(Regexes.CREA)
			pass
		else: # unknown reply
			print("[ UNK ] [%s] %s" % (num, reply))

