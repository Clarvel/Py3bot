
"""
matthew russell
june 25, 2015
parent class for IRC channels and clients

"""
from logger import Logger

class IRCReceiver():
	def __init__(self, name, host):
		self.name = name
		self._logger = Logger("%s/%s" % (host, self.name))

	def __str__(self):
		return self.name

	def log(self, message):
		self._logger.log(message)
		print("[%s]%s" % (self.name, message))

	def sendMessage(self, message, receiver):
		pass
		#self.server.sendMessage(message, receiver)

class IRCChannel(IRCReceiver):
	def __init__(self, name, host, topic='No topic'):
		super().__init__(name, host)
		self.topic = topic
		self.users = [] # [user, [modes]]
		self.modes = []
		self.type = None

	def delUser(self, user):
		for u in self.users:
			if u[0] == user:
				self.users.remove(u)

	def addUser(self, user, mode=""):
		for u in self.users:
			if u[0] == user:
				return
		self.users.append([user, mode])

	def setUserMode(self, user, mode):
		for u in self.users:
			if u[0] == user:
				u[1] = mode
				return

class IRCClient(IRCReceiver):
	def __init__(self, name, host):
		super().__init__(name, host)
		self.loginName = "Unknown"
		self.address = "Unknown"
		self.realName = "Unknown"
		self.channels = []
		self.signOn = None
		self.silenced = False

	def addChannel(self, channel):
		try:
			self.channels.index(channel)
		except Exception:
			self.channels.append(channel)

	def delChannel(self, channel):
		try:
			self.channels.remove(channel)
		except ValueError:
			pass



