
import socket
import threading
from Regexes import REMatch
import re

PING_PAT = re.compile(r':?PING(.*)')

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
	def __init__(self, logger, name):
		self.logger = logger
		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.connection.settimeout(40)
		self.name = name

		self.chanList = {}
		self.chanKey = None

		self.closed = True

	def connect(self, host, port, password=None):
		# connect to server

		if(not self.closed):
			self.logger.error("Server already connected")
			return

		serv_addr = (host, port)
		try:
			self.connection.connect(serv_addr)
		except Exception as e:
			self.logger.error("Connection to host %s failed: %s" % (host, str(e)))
		else:
			self.closed = False
			self.logger.info('Connected to %s:%d' % (serv_addr))

			if password != None:
				print(password)
				self.sendData("PASS %s" % (password))

			self.sendData("USER %s %s * :%s" % (self.name, socket.gethostname(), self.name))
			self.sendData("NICK %s" % (self.name))

			self.listenThread = threading.Thread(target=self.listen) # spawn listening thread
			self.listenThread.daemon = True # ensure thread dies when main thread dies
			self.listenThread.start() # start listening thread

	def close(self, message = ""):
		#closes with optional message
		self.sendData("QUIT %s" % (message))
		self.closed = True

	def listen(self):
		loop = True
		while loop:
			try:
				chunk = self.connection.recv(4096).decode('UTF-8').rstrip()
			except Exception as e:
				self.logger.error("Connection to host failed: %s" % (str(e)))
				loop = False
			else:
				self.logger.info("RESP: %s" % chunk)
				actionThread = threading.Thread(target=self.performAction, args=(chunk,))
				actionThread.daemon = True
				actionThread.start()
		self.close()

	def sendData(self, msg):
		#Send msg over the connection socket to server
		try:
			#print(msg)
			sent = self.connection.send(bytes("%s\r\n" % (msg), 'UTF-8'))
			if sent == 0:
				raise RuntimeError("Socket Connection Broken")
		except Exception as e:
			self.logger.error("Could not send data: %s" % e)

	def sendMsg(self, msg, channel = None):
		if(channel == None): # default to current channel if no chan specified
			try:
				channel = self.chanList[self.chanKey]
			except Exception as e:
				self.sendPM(msg)
				return
		# send data to channel
		self.sendData("PRIVMSG %s :%s" % (channel, msg))

	def sendPM(self, msg, receiver = None):
		if(receiver == None):
			self.sendData(msg)
			return
		# send data to person
		self.sendData("PRIVMSG %s :%s" % (receiver, msg))

	def nick(self, name):
		self.name = name
		# set nickname for bot
		self.sendData("NICK %s" % (self.name))

	def performAction(self, chunk):
		"""Perform some action based on the command fed to the bot"""
		_m = REMatch(chunk)
		if _m.match(PING_PAT):
			self.sendData("PONG %s" % (_m.group(1).strip()))

	def channel(self, name, chanID=None, password = ""):
		if(chanID == None):
			chanID = name
		#joins channel
		print("test")
		self.sendData("JOIN %s %s" % (name, password))
		self.chanKey = chanID
		self.chanList[chanID] = name

	def swapChan(self, chanID):
		if chanID in self.chanList.keys():
			self.chanKey = chanID
			print("Setting active Channel to %s" % (self.chanKey))
		else:
			self.logger.error("Bad channel key: %s" % (chanID))

	def closeChan(self, chanID):
		# leaves channel
		if chanID in self.chanList.keys():
			self.sendData("PART %s" % (self.chanList[chanID]))
			del self.chanList[servID]

			if(chanID == self.chanKey):
				self.chanKey = self.chanList.keys()[0]
				print("Setting active Channel to %s" % (self.chanKey))
		else:
			self.logger.error("Bad channel key: %s" % (chanID))



