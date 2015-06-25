"""
IRC server class
Matthew Russell
last updated June 25, 2015

implements commands to send to server
https://en.wikipedia.org/wiki/List_of_Internet_Relay_Chat_commands
"""
from IRCerrors import IRCError, IRCServerError
from IRCserver import IRCServer

class IRCServerCommands(IRCServer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._methods = {
			"":self._message,
			"pm":self.message,
			"msg":self.message,
			"me":self._action,
			"ignore":self.silence,
		}
	# TODO: find a way to detect message parameter: join message string together

	def commandParser(self, command, options):
		"""
		parses commands, shouldn't be called directly from terminal
		"""
		try:
			getattr(self, command)(*options)
		except AttributeError as e:
			if command in self._methods:
				self._methods[command](*options)
			else:
				raise IRCServerError("Command not found! %s" % e)


	def nick(self, name):
		"""
		sends nick message
		"""
		self.sendData("NICK %s" % (name))

	def join(self, channel, password=""):
		""" Join channel, optionally with password. """
		try:
			receiver = self.getReceiver(channel)
		except IRCError:
			self.sendData('JOIN %s %s' % (channel, password))
		else:
			self.logE("Already in channel [%s]" % (channel))

	def part(self, channel=None, *message):
		""" Leave channel, optionally with message. """
		try:
			channel = self.getChannel(channel)
		except IRCError:
			message = list(message)
			message.insert(0, channel)
			try:
				channel = self.getChannel()
			except IRCError as e:
				self.logE("No such channel: %s" % (e))
			else:
				self.sendData('PART %s %s' % (channel, " ".join(message)))
		else:
			self.sendData('PART %s :%s' % (channel, " ".join(message)))

	def kick(self, target, channel=None, *reason):
		""" Kick user from channel. """
		try:
			target = self.getClient(target)
		except IRCError as e:
			self.logE("Client not found: %s" % (e))
		else:
			try:
				channel = self.getChannel(channel)
			except IRCError:
				reason = list(reason)
				reason.insert(0, channel)
				try:
					channel = self.getChannel()
				except IRCError as e:
					self.logE("Channel not found: %s" % (e))
				else:
					self.sendData('KICK %s %s :%s' % (channel, target, 
					" ".join(reason)))
			else:
				self.sendData('KICK %s %s :%s' % (channel, target, 
					" ".join(reason)))

	def ban(self, target, channel=None, range=0):
		"""
		Ban user from channel. Target can be either a user or a host.
		This command will not kick: use kickban() for that.
		range indicates the IP/host range to ban: 0 means ban only the IP/host,
		1+ means ban that many 'degrees' (up to 3 for IP addresses) of the host for range bans.
		"""
		# TODO masking on target string
		self.setMode("+b", target, channel)

	def unban(self, target, channel=None, range=0):
		"""
		Unban user from channel. Target can be either a user or a host.
		See ban documentation for the range parameter.
		"""
		# TODO masking on target string
		self.setMode("-b", target, channel)

	def kickban(self, target, channel=None, range=0, *reason):
		"""
		Kick and ban user from channel.
		"""
		self.ban(target, channel, range)
		self.kick(target, channel, reason)

	def quit(self, *message):
		""" Quit network. """
		self.disconnect(" ".join(message))

	def message(self, target, *message):
		""" Message channel or user. """
		try:
			target = self.getReceiver(target)
		except IRCError as e:
			self.logE("No such nick/channel: %s" % (e))
		else:
			self.sendData("PRIVMSG %s :%s" % (target, " ".join(message)))

	def _message(self, *message):
		""" Message current channel or user. """
		try:
			target = self.getReceiver()
		except IRCError as e:
			self.logE("No such nick/channel: %s" % (e))
		else:
			self.sendData("PRIVMSG %s :%s" % (target, " ".join(message)))

	def action(self, target, *message):
		self.message(target, "\x01ACTION %s\x01" % " ".join(message))

	def _action(self, *message):
		""" /me command """
		# default to current channel if no chan specified
		self._message("\x01ACTION %s\x01" % " ".join(message))

	def notice(self, target=None, *message):
		""" Notice channel or user. """
		#TODO verify message length here or?
		try:
			target = self.getReceiver(target)
		except IRCError:
			message = list(message)
			message.insert(0, target)
			try:
				target = self.getReceiver()
			except IRCError as e:
				self.logE("No such nick/channel: %s" % (e))
			else:
				self.sendData("NOTICE %s %s" % (target, 
					" ".join(message)))
		else:
			self.sendData("NOTICE %s %s" % (target, 
				" ".join(message)))

	def mode(self, mode, target=None, channel=None):#TODO
		"""
		Set mode on target.
		Users should only rely on the mode actually being changed when receiving an on_{channel,user}_mode_change callback.
		"""
		try:
			target = self.getClient(target)
		except IRCError:
			target = ""
		try:
			channel = self.getChannel(channel)
		except IRCError as e:
			self.logE("Channel not found: %s" % (e))
		else:
			# TODO ensure proper modes set
			self.sendData('MODE %s %s %s' % (channel, mode, target))

	def topic(self, channel=None, *topic):
		"""
		Set topic on channel.
		Users should only rely on the topic actually being changed when receiving an on_topic_change callback.
		"""
		try:
			channel = self.getChannel(channel)
		except IRCError:
			topic = list(topic)
			topic.insert(0, channel)
			try:
				channel = self.getChannel()
			except IRCError as e:
				self.logE("No such channel: %s" % (e))
			else:
				self.sendData('TOPIC %s :%s' % (channel, " ".join(topic)))
		else:
			self.sendData('TOPIC %s :%s' % (channel, " ".join(topic)))

	def away(self, *message):
		""" Mark self as away. """
		self.sendData('AWAY %s' % " ".join(message))

	def back(self):
		""" Mark self as not away. """
		self.sendData('AWAY')

	def whois(self, target):
		"""
		Return information about user.
		"""
		try:
			target = self.getClient(target)
		except IRCError as e:
			self.logE("No such client: %s" % (e))
		else:
			self.sendData('WHOIS', target)

	def whowas(self, target):
		"""
		Return information about an offline user.
		no checking on this because offline users won't be in my data
		"""
		self.sendData('WHOWAS %s' % target)

	def admin(self):
		"""should return server's administrator information"""
		self.sendData('ADMIN')

	def cnotice(self, target, channel=None, *message):
		"""send channel notice"""
		try:
			target = self.getClient(target)
		except IRCError as e:
			self.logE("Client not found: %s" % (e))
		else:
			try:
				channel = self.getChannel(channel)
			except IRCError:
				message = list(message)
				message.insert(0, channel)
				try:
					channel = self.getChannel()
				except IRCError as e:
					self.logE("Channel not found: %s" % (e))
				else:
					self.sendData('CNOTICE %s %s :%s' % (channel, target, 
					" ".join(message)))
			else:
				self.sendData('CNOTICE %s %s :%s' % (channel, target, 
					" ".join(message)))

	def cprivmsg(self, target, channel = None, *message):
		"""send pm to target on channel"""
		try:
			target = self.getClient(target)
		except IRCError as e:
			self.logE("Client not found: %s" % (e))
		else:
			try:
				channel = self.getChannel(channel)
			except IRCError:
				message = list(message)
				message.insert(0, channel)
				try:
					channel = self.getChannel()
				except IRCError as e:
					self.logE("Channel not found: %s" % (e))
				else:
					self.sendData('CPRIVMSG %s %s :%s' % (channel, target, 
					" ".join(message)))
			else:
				self.sendData('CPRIVMSG %s %s :%s' % (channel, target, 
					" ".join(message)))

	def help(self):
		"""request help from server"""
		self.sendData("HELP")

	def info(self):
		"""request help from server"""
		self.sendData("INFO")

	def ison(self, *message):
		"""check nicknames in list are on network"""
		self.sendData("ISON %s" % " ".join(list(message)))

	def kill(self, target, *message):#TODO
		"""
		forcibly removes client from network
		only for use by IRC ops
		"""
		self.sendData("KILL %s %s" % (target, " ".join(list(message))))

	def knock(self, channel, *message):#TODO
		"""notice to invite only channel with message"""
		self.sendData("KNOCK %s %s" % (channel, " ".join(list(message))))

	def list(self, *channels):
		"""
		lists all channels on server
		if channels is given, returns channel topics
		"""
		self.sendData("LIST %s" % ", ".join(list(channels)))

	def motd(self):
		"""returns message of the day"""
		self.sendData("MOTD")

	def names(self, *channels):
		"""returns list of who's on channels, or all users"""
		self.sendData("NAMES %s" % ", ".join(list(channels)))

	def oper(self, target, password):
		"""authenticates user with password"""
		self.sendData("OPER %s %s" % (target, password))

	def ping(self):
		"""pings server connection"""
		self.sendData("PING %s" % self.getHost())

	def rules(self):
		"""returns rules of the server"""
		self.sendData("RULES")

	def servlist(self):
		"""returns services on network"""
		self.sendData("SERVLIST")

	def squery(self, service, *message):
		"""sends pm to service"""
		self.sendData("SQUERY %s %s" % (service, " ".join(list(message))))

	def setname(self, name):
		"""sets server's stored real name"""
		self.sendData("SETNAME %s" % name)

	def silence(self, target = ""):
		"""
		prevents target from sending me messages
		if target not given, list all ignored targets
		prefix = [+, -]
		"""
		prefix = ""
		if target:
			try:
				target = self.getClient()
			except IRCError as e:
				self.logE("No client found: %s" % e)
			else:
				if(target.silenced):
					prefix = '-'
				else:
					prefix = '+'
		self.sendData("SILENCE %s%s" % (prefix, target))

	def stats(self):
		"""returns stats about the server"""
		self.sendData("STATS")

	def time(self):
		"""returns local time of the server"""
		self.sendData("TIME")

	def uhnames(self):
		"""returns names in long format"""
		self.sendData("PROTOCTL UHNAMES")

	def userhost(self, target):
		"""returns list of info about nickname given"""
		try:
			target = self.getClient(target)
		except IRCError as e:
			self.logE("Client %s not found: %s" % (target, e))
		else:
			self.sendData("USERHOST %s" % target)

	def userIP(self, target):
		"""returns direct IP of target"""
		try:
			target = self.getClient(target)
		except IRCError as e:
			self.logE("Could not find target: %s" % (e))
		else:
			self.sendData("USERIP %s" % target)

	def users(self):
		"""returns list of users and info about them"""
		self.sendData("USERS")

	def version(self):
		"""returns version of server"""
		self.sendData("VERSION")

	def wallops(self, *message):
		"""sends message to all ops with mode w"""
		self.sendData("WALLOPS %s" % " ".join(list(message)))

	def whop(self, target):
		"""returns list of ops matching target"""
		self.sendData("WHO %s o" % target)

	def who(self, target):
		"""returns list of users matching target"""
		self.sendData("WHO %s" % target)





