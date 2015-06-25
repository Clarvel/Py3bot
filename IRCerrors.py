"""
matthew russell
june 25, 2015
errors for IRC classes
"""

class IRCError(Exception):
	"""
	Exception thrown by IRC command handlers to notify client of a
	server/client error.
	"""
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "[ERROR]: %s" % (self.value)

class IRCServerError(IRCError):
	def __str__(self):
		return "[SERVER ERROR]: %s" % self.value

class IRCBotError(IRCError):
	def __str__(self):
		return "[BOT ERROR]: %s" % self.value
		
class IRCIOError(IRCError):
	def __init__(self, value, host):
		self.value = "Connection to %s failed: %s" % (host, value)

class IRCModError(IRCError):
	def __str__(self):
		return "[MOD ERROR]: %s" % self.value
