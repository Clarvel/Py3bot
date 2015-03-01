"""
IRC terminal client class
Matthew Russell
last updated feb 28, 2015

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

	def listen(self):
		# setup terminal input loop
		self.loop = True
		while(self.loop): # listen for input and then parse input forver
			a = input("")
			self.termParser(a)

	def termParser(self, msg): # parses terminal input
		try: # try to handle message
			if(msg.startswith('/')): 	# matches a terminal command
				options = msg.split() # split by whitespace
				cmd = options.pop(0) # first option is the possible command
				cmd = cmd.split('/', 1)[1] # remove terminal command char
				# try to match cmd to a function
				if cmd == "quit":
					self.bot.quit(" ".join(options))
					self.loop = False
				elif cmd == "this":
					server = self.bot.servKey
					if(server == None):
						server = "None"
						channel = "None"
					else:
						channel = self.bot.getServ().chanKey
						if(channel == None):
							channel = "None"

					print("@[%s %s]" % (server, channel))
				else: # it's a server message
					self.bot.termCmd(cmd, options)
			else: # else send message to server
				self.bot.termMsg(msg)		
		except Exception as e:
			print("[ERROR] terminal Parser failed: %s" % (e))
