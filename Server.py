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

from IRCconnection import IRCConnection
from Logger import Logger
from Channel import Channel
from Settings import SETTINGS

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
	def __init__(self, host, port, nickName, serverPrepend = "", password = None, quitMessage = ""):
		self.host = host
		self.port = port
		self.name = nickName
		self.servPre = serverPrepend
		self.password = password
		self.quitMsg = quitMessage
		self.chanList = {}
		self.chanKey = None
		self.chanIDList = {}
		self.pmIDList = {}
		self.closed = True

		self.connection = IRCConnection(self.host, self.port, self.nick, self.parseInput)	

		self.logger = Logger("%s/%s" % (self.host, self.host), serverPrepend)
		self.connect()

	def connect(self):
		try:
			self.connection.connect()
		except Exception as e:
			self.logger.error("Connection to host %s failed: %s" % (self.host, str(e)))
		else:
			self.logger.info('Connected to %s:%d' % (self.host, self.port))
			self.closed = False


	def stop(self, message = None):
		#closes with optional message
		if message == None:
			message = self.quitMsg
		for channel in self.chanList.keys(): # log quit messages
			self.chanList[channel].log("QUIT %s" % (message))
		for pmKey in self.pmIDList.keys(): # log quit messages
			self.pmIDList[pmKey].log("QUIT %s" % (message))
		self.logger.log("QUIT %s" % (message))
		self.connection.disconnect()

	def newChannel(self, name, channelID = None, password = "", log = True, bannedMods = None):
		if(channelID == None):
			channelID = name

		# make new channel class
		newChan = Channel(name, self.host, self.sendMsg, "%s %s" % (self.servPre, channelID), log, bannedMods)

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
			tmp = Channel(name, self.host, self.sendMsg, "%s %s" % (self.servPre, name), True, None)
			self.chanIDList[name] = tmp
			private = tmp
		return private

	def getChannelKey(self): # return current channel key
		if(self.chanKey == None):
			return "None"
		return self.chanKey

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
				print("PINGED: %s" % msg.group(1))
			elif msg.match(Regexes.USER): # string matched user message
				smsg = Regexes.REMatch(msg.group(4))
				if   smsg.match(Regexes.PMSG): # submessage matched private message
					ssmsg = Regexes.REMatch(smsg.group(2))
					if ssmsg.match(Regexes.ACTN): # subsubmessage matched action
						chan = self.getPrivateName(smsg.group(1)) # find appropriate channel
						if self.name in smsg.group(2): # if mentioned
							return chan.mtn(msg.group(1), smsg.group(2))
						else:
							return chan.act(msg.group(1), ssmsg.group(1))
					else: # it's a private/channel message
						if(smsg.group(1) != self.name): # if target is not me
							chan = self.getPrivateName(smsg.group(1)) # find appropriate channel
						else: # target is me, its a PM
							chan = self.getPrivateName(msg.group(1))
							if self.loginAdmin(msg.group(1), "%s@%s" % (msg.group(2), msg.group(3)), smsg.group(2)): # test if admin command
								return # if successfully logged in admin, stop parsing
						
						reply = None
						try: # try to find command, if not found continue as normal
							if self.admin != None and self.admin == ("%s@%s" % (msg.group(2), msg.group(3))): # admin said something
								options = smsg.group(2).split()
								cmd = options.pop(0)
								reply = self.clientCommand(cmd, options)
							else:
								raise Exception("not Admin")
						except Exception as e:
							#do nothing
							pass
						else: # if task found and completed, send msg and stop parsing
							if reply != None:
								chan.log("%s: %s" % (msg.group(1), smsg.group(2)))
								replies = reply.split("\n")
								for reply in replies:
									self.sendMsg(reply, chan.name)
							else:
								self.sendMsg("It is done", chan.name)
							return

						if self.name in smsg.group(2): # if mentioned
							return chan.mtn(msg.group(1), smsg.group(2))
						else:
							return chan.msg(msg.group(1), smsg.group(2))
				elif smsg.match(Regexes.JOIN):
					chan = self.getPrivateName(smsg.group(1)) # find appropriate channel
					return chan.log("%s joined %s" % (msg.group(1), smsg.group(1))) # TODO
				elif smsg.match(Regexes.NICK):
					self.logger.info("%s is now known as %s" % (msg.group(1), smsg.group(1)))
					#TODO for all channels and pms containing this nick, change their values
				elif smsg.match(Regexes.QUIT):
					self.logger.info("%s quit: %s" % (msg.group(1), smsg.group(1)))
					# TODO propagate this thru all relevant channels
				elif smsg.match(Regexes.PART):
					chan = self.getPrivateName(smsg.group(1))
					return chan.log("%s left: %s" % (msg.group(1), smsg.group(2))) # TODO
				elif smsg.match(Regexes.MODE):
					chan = self.getPrivateName(smsg.group(1))
					return chan.log("%s set mode %s %s" % (msg.group(1), smsg.group(2), smsg.group(3)))
				elif smsg.match(Regexes.NTCE):
					chan = self.getPrivateName(smsg.group(1))
					return chan.log("Notice from %s: %s" % (msg.group(1), smsg.group(2))) # TODO
				elif smsg.match(Regexes.INVT):
					chan = self.newChannel(smsg.group(1)) # join new channel
				else:
					return("[ ERR ][UNKNOWN USER STRING]%s" % string)
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
					return("[ ERR ][UNKNOWN SERVER STRING]" % string)
			else:
				return("[ ERR ][UNKNOWN STRING]%s" % string)


	def sendData(self, msg):
		#Send msg over the connection socket to server
		try:
			#print(msg)
			sent = self.connection.sendData(msg)
		except Exception as e:
			return self.logger.error("Could not send data: %s" % e)

	def sendMsg(self, msg, receiver = None): # send message to channel specified or to current channel otherwise
		if(receiver == None): # default to current channel if no chan specified
			receiver = self.getChannel().getName() # get channel value
		# send data to channel
		self.getPrivateName(receiver).log("%s: %s" % (self.name, msg)) # log message through channel class
		return self.sendData("PRIVMSG %s %s" % (receiver, msg))

	def nick(self, name = None): # change given nickname
		if(not name):
			return self.name
		# set nickname for bot
		try:
			a = self.sendData(":%s NICK %s" % (self.name, name))
		except Exception as e:
			return a
		else:
			self.name = name


	def clientCommand(self, cmd, options): # command received from client
		if   cmd == "join" or cmd =="c" or cmd == "channel":
			return self.newChannel(*options)
		elif cmd == "setch"	or cmd == "sc":
			return self.swapChannel(*options)
		elif cmd == "part":
			channel = options.pop(0)
			msg = None
			if(len(options) > 0):
				msg = " ".join(options)
			return self.closeChannel(channel, msg)
		else:
			# send message to current server
			optStr = " ".join(options) # preconcat message

			if   cmd == "pm":
				return self.sendData("PRIVMSG %s" % (optStr))
			elif cmd == "notice" or cmd == "n":
				return self.sendData("NOTICE %s" % (optStr))
			elif cmd == "reply" or cmd == "r":
				pass # TODO
				return self.sendData("%s" % (optStr))
			elif cmd == "me":
				return self.sendMsg("\x01" + "ACTION %s\x01" % (optStr))
			elif cmd == "oper": 
				return self.sendData("OPER %s" % optStr)
			elif cmd == "mode":
				return self.sendData("MODE %s %s" % (self.getChannel(), optStr))
			elif cmd == "topic" or cmd == "t":
				if(len(options) == 0):
					return self.sendData("TOPIC %s" % (self.getChannel()))
				else:
					return self.sendData("TOPIC %s :%s" % (self.getChannel(), optStr))
			elif cmd == "names":
				return self.sendData("NAMES %s" % (self.getChannel()))
			elif cmd == "nick":
				if(len(options) == 0):
					return("Nickname: [%s]" % self.name)
				else:
					return self.nick(optStr)
			elif cmd == "invite" or cmd == "inv" or cmd == "i":
				if(len(options) > 1):
					return self.sendData("INVITE %s" % (optStr)) # assume channel specified
				else:
					return self.sendData("INVITE %s %s" % (optStr, self.getChannel()))
			elif cmd == "kick" or cmd == "k":
				return self.sendData("KICK %s %s :%s" % (self.getChannel(), options.pop(0), " ".join(options)))
			elif cmd == "whois":
				return self.sendData("WHOIS %s" % (optStr))
			elif cmd == "whowas":
				return self.sendData("WHOWAS %s" % (optStr))
			elif cmd == "kill":
				return self.sendData("KILL %s" % (optStr))
			else:
				return self.getChannel().clientCommand(cmd, options)

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
			self.getPrivateName(msg.group(1)).log("TOPIC: %s" % msg.group(2))
		elif num == 333: # creator
			#msg.match(Regexes.CREA)
			pass
		else: # unknown reply
			print("[ UNK ] [%s] %s" % (num, reply))


	def loginAdmin(self, sender, IP, message):
		message = message.split()
		try:
			if message[0] == "ADMIN" and message[1] == SETTINGS["ADMIN_PASSWORD"] and SETTINGS["ADMIN_PASSWORD"] != "" and SETTINGS["ADMIN_PASSWORD"] != None:
				self.admin = IP
				self.getPrivateName(sender).log("%s: %s" % (sender, " ".join(message)))
				self.sendMsg("Hello, Master", sender)
				return True
		except Exception as e:
			return False
		return False

