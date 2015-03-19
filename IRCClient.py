"""
IRC terminal client class
Matthew Russell
last updated mar 5, 2015

class instances the IRC bot
listens for terminal input
parses commands and passes them to the IRC bot

initialize with 
	a=IRCClient()
start with
	a.listen()
"""

from Bot import Bot

class IRCClient(): # IRC terminal client class
	def __init__(self):
		self.bot = Bot() # instance the bot
		self.keepListening = False

	def listen(self):
		# setup terminal input loop
		self.keepListening = True
		while(self.keepListening): # listen for input and then parse input forver
			a = input("")
			self.terminalParser(a)

	def terminalParser(self, msg): # parses terminal input
		try: # try to handle message
			if(msg.startswith('/')): # matches a terminal command
				options = msg.split() # split by whitespace
				cmd = options.pop(0) # first option is the possible command
				cmd = cmd.split('/', 1)[1] # remove terminal command char
				# try to match cmd to a function
				if cmd == "quit":
					msg = None
					if(len(options) > 0):
						msg = " ".join(options) 
					self.bot.quit(msg)
					self.keepListening = False
				elif cmd == "this" or cmd == "context":
					print("@[%s %s]" % (self.bot.getServerKey(), self.bot.getServer().getChannelKey()))
				elif cmd == "help" or cmd == "h":
					#TODO
					print("Help is on the way!")
				else: # it's a server message
					tMsg = self.bot.clientCommand(cmd, options)
					if tMsg != None and tMsg != "None":
						print(tMsg)
			else: # else send message to server
				self.bot.clientMessage(msg)		
		except Exception as e:
			print("[ERROR]: %s" % (e))
