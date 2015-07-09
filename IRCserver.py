"""
IRC server class
Matthew Russell
last updated June 29, 2015

class handles communication between the IRC bot and the connection and 
variables and fucntions associated with an IRC server

"""

import socket
import threading

from cycle import Cycle
from logger import Logger
from IRCerrors import IRCServerError
from connection import Connection
from IRCreceivers import IRCChannel, IRCClient, IRCReceiver
from settings import CHANNEL_PREFIXES, MESSAGE_LENGTH_LIMIT, REAL_NAME, LOGIN_NAME, NICKNAMES

class IRCServer():
	"""
	class for connecting to an IRC server
	1 server per connection
	"""
	_reconnectTimeout = 300


	def __init__(self, host, port, terminalID = "", password = None):
		self.receivers = {}
		self.quitMessage = ""
		self.password = password
		self.nickNames = Cycle(NICKNAMES)

		self._terminalID = terminalID # shorthand for server in terminal
		self._currentReceiverKey = None
		self._connection = Connection(host, port, self._parseInput)
		self._logger = Logger("%s/%s" % (host, "SERVER"))
		self._clientObject = self._newReceiver(self.nickNames.val())
		self._welcomeEvent = threading.Event()
		self._reconnectEvent = threading.Event()
		self._reconnectEvent.set()

	#-------------------------------------------------------------------------

	def connect(self):
		"""
		connect to the host/port
		raises error on fail
		"""
		try:
			connection = self._connection.connect()
		except Exception as e:
			raise IRCServerError("Connection failed: [%s] %s"%(e.__name__, e))

		if(self.password):
			self.sendRaw("PASS %s" % (self.password))
		self.sendRaw("NICK %s" % self.nickNames.val())
		self.sendRaw("USER %s %s * :%s"%(LOGIN_NAME, socket.gethostname(), 
			REAL_NAME))

		self._welcomeEvent.clear()
		self._welcomeEvent.wait()

	def disconnect(self, message = None):
		if(self.isConnected()):
			if not message:
				message = self.quitMessage
			self.sendCmd("QUIT", None, message)
		self._connection.disconnect()

	def reconnect(self):
		"""
		reconnecting function
		prevents multiple threads from trying to reconnect at once
		pauses all reconnect tries until reconnect succeeds or fails
		"""
		if not self._reconnectEvent.is_set():
			self._reconnectEvent.wait()
		else:
			self._reconnectEvent.clear()
			self.disconnect()
			error = None
			for timer in range(5, self._reconnectTimeout, 15):
				self.log("Reconnecting...")
				try:
					self.connect()
				except Exception as e:
					error = e
					time.sleep(timer)
				else:
					break
			else:
				self.logE("Reconnect failed after %ds: %s"%(timer/60, error))
			self._reconnectEvent.set()

	#-------------------------------------------------------------------------

	def sendRaw(self, data):
		"""sends raw data strings to the server connection"""
		try:
			self._connection.send(data.rstrip())
		except Exception as e:
			self.reconnect()

			self.logE("Data send failed: %s" % e)

	def sendCmd(self, command, meta=None, *message): # TODO limit message length my receiver's full name@host
		"""
		sends command with optional meta data and message
		will split messages to ensure they're under the maximum length
		"""
		if meta:
			if isinstance(meta, list):
				meta = " ".join(meta)
			command = "%s %s" % (command, meta)
		if message:
			msg = " ".join(list(message))
			strLim = MESSAGE_LENGTH_LIMIT - (len(command) + 2)
			a=0
			for a in range(strLim, len(msg), strLim):
				self.sendRaw("%s :%s" % (command, msg[a-strLim:a]))
			self.sendRaw("%s :%s" % (command, msg[a:len(msg)]))
		else:
			self.sendRaw(command)

	def _parseInput(self, line):
		"""overloadable function to receive commands from conected server"""
		self.log(line)

	#-------------------------------------------------------------------------
	
	def _newReceiver(self, name):
		if any(name.startswith(prefix) for prefix in CHANNEL_PREFIXES):
			newRec = IRCChannel(name, self._connection.host)
		else:
			newRec = IRCClient(name, self._connection.host)
		self.receivers[name.lower()] = newRec
		if len(self.receivers) == 1:
			self.swapCurrentReceiver(name)
		return newRec

	def _delReceiver(self, name):
		"""
		removes the specified receiver from the list
		"""
		self.receivers.pop(name.lower())

	def _renameReceiver(self, oldName, newName):
		"""
		renames the receiver and alters the key to it
		"""
		old = self.receivers.pop(oldName.lower())
		old.name = newName
		self.receivers[newName.lower()] = old


	def swapCurrentReceiver(self, name):
		name = name.lower()
		if name in self.receivers:
			self._currentReceiverKey = name
		else:
			raise IRCServerError("Unknown user/channel: %s" % name)

	def listReceivers(self):
		return [b.name for b in self.receivers.values()]

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
			name = str(name)
		name = name.lower()
		try:
			receiver = self.receivers[name]
		except KeyError as e:
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





