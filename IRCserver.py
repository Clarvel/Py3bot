"""
IRC server class
Matthew Russell
last updated June 25, 2015

class handles communication between the IRC bot and the connection and 
variables and fucntions associated with an IRC server

"""

from logger import Logger
from IRCerrors import IRCServerError
from IRCconnection import IRCConnection
from IRCreceivers import IRCChannel, IRCClient, IRCReceiver
from settings import CHANNEL_PREFIXES

class IRCServer():
	"""
	class for connecting to an IRC server
	1 server per connection
	"""

	def __init__(self, host, port, nickName, terminalID = "", password = None):
		self.receivers = {}
		self.quitMessage = ""
		self._terminalID = terminalID # shorthand for server in terminal
		self._currentReceiverKey = None

		self._connection = IRCConnection(host, port, self.getNick, 
			self._parseInput, password)

		self._logger = Logger("%s/%s" % (host, "SERVER"))

		self._clientObject = self._newReceiver(nickName)

	#-------------------------------------------------------------------------

	def connect(self):
		"""
		connect to the host/port
		"""
		try:
			connection = self._connection.connect()
		except Exception as e:
			self.logE("Connection Failed: %s" % e)
		else:
			self.log('Connected to %s' % (connection))

	def disconnect(self, message = None):
		if(self.isConnected()):
			if not message:
				message = self.quitMessage
			#self.log("QUIT %s" % (message))
			self._connection.disconnect(message)

	def reconnect(self):
		try:
			connecton = self._connection.reconnect()
		except Exception as e:
			self.logE("Reconnect failed: " % e)
		else:
			self.log('Reconnected to %s' % (connection))

	#-------------------------------------------------------------------------

	def sendData(self, data):
		try:
			self._connection.sendData(data.rstrip())
		except Exception as e:
			self.logE("Data send failed: %s" % e)

	def _parseInput(self, line):
		"""overloadable function to receive commands from conected server"""
		self.log(line)

	#-------------------------------------------------------------------------
	
	def _newReceiver(self, name):
		if any(name.startswith(prefix) for prefix in CHANNEL_PREFIXES):
			newRec = IRCChannel(name, self._connection.host)
		else:
			newRec = IRCClient(name, self._connection.host)
		self.receivers[name] = newRec
		if len(self.receivers) == 1:
			self.swapCurrentReceiver(name)
		return newRec

	def _delReceiver(self, name):#TODO
		""""""
		pass

	def swapCurrentReceiver(self, name):
		if name in self.receivers:
			self._currentReceiverKey = name
		else:
			raise IRCServerError("Unknown user/channel: %s" % name)

	#-------------------------------------------------------------------------

	def getReceiver(self, name=None):
		"""
		returns a Receiver class object 
		if no name specified, uses the current receiver
		"""
		if not name:
			if(not self._currentReceiverKey):
				raise IRCServerError("No known channels/users for this Server!")
			return self.receivers[self._currentReceiverKey]
		elif isinstance(name, IRCReceiver):
			name = name.name
		try:
			receiver = self.receivers[name]
		except KeyError as e:
			for receiver in self.receivers:
				if(receiver == name):
					return receiver
			raise IRCServerError("No channel/user found matching [%s]" % (name))
		else:
			return receiver

	def getChannel(self, name=None):
		receiver = self.getReceiver(name)
		if(isinstance(receiver, IRCChannel)):
			return receiver
		raise IRCServerError("[%s] is not a channel" % name)

	def getClient(self, name=None):
		receiver = self.getReceiver(name)
		if(isinstance(receiver, IRCClient)):
			return receiver
		raise IRCServerError("[%s] is not a client" % name)

	#-------------------------------------------------------------------------

	def isConnected(self):
		""""""
		return self._connection.isConnected()

	def getHost(self):
		"""returns host string"""
		return self._connection.host

	def getNick(self):
		"""returns the current nickname"""
		return self._clientObject.name

	#-------------------------------------------------------------------------

	def log(self, message):
		self._logger.log(message)
		print("[%s]%s" % (self._terminalID, message))

	def logE(self, message):
		self.log("[ERROR]: %s" % (message))





