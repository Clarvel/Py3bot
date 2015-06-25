"""
IRC terminal client class
Matthew Russell
last updated june 25, 2015

class instances the IRC bot
listens for terminal input
parses commands and passes them to the IRC bot

initialize with 
	a=IRCClient()
start with
	a.start()
"""

from IRCerrors import IRCError

class TerminalListener():
	"""IRC terminal client class"""
	def __init__(self, commandCallback, terminalPromptCallback):
		self._commandCallback = commandCallback
		self._terminalPromptCallback = terminalPromptCallback
		self._keepListening = False
		self._terminalCommand = '/'

	def start(self):
		"""starts listening to terminal"""
		self._listen()

	def stop(self):
		"""stops the listening thread"""
		self._keepListening = False

	def _listen(self):
		"""setup terminal input loop"""
		self._keepListening = True
		while(self._keepListening):
			#self._terminalPromptCallback()))
			a=input("")
			"""
			thread = threading.Thread(target=self._parser, args=(a,))
			thread.daemon = True
			thread.start()
			"""
			self._parser(a)

	def _parser(self, msg):
		"""Parses for the command and splits options"""
		command = ""
		options = msg.split()
		if(msg.startswith(self._terminalCommand)):
			command = options.pop(0)
			command = command.split('/', 1)[1]
		try: # try to handle message
			self._commandCallback(command, options)
		except IRCError as e:
			print("[%s]" % e)
		except Exception as e:
			print("[TERMINAL ERROR]: %s" % (e))
