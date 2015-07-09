"""
IRC server class
Matthew Russell
last updated June 29, 2015

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
			"privmsg":self.message,
		}
	# TODO: find a way to detect message parameter: join message string together

	def commandParser(self, command, options):
		"""
		parses commands, shouldn't be called directly from terminal
		"""
		try:
			return getattr(self, command)(*options)
		except AttributeError as e:
			if command in self._methods:
				return self._methods[command](*options)
			else:
				raise IRCServerError("Command not found! %s" % e)
		except IRCServerError as e:
			return "[IRCServerError]: %s" % (e)


	def nick(self, name):
		"""
		sends nick message
		"""
		self.sendCmd("NICK", name)

	def join(self, channel, password=""):
		""" 
		Join channel, optionally with password. 
		does not check for already joined if multiple channels/passwords given
		"""
		try:
			receiver = self.getReceiver(channel)
		except IRCError:
			self.sendCmd('JOIN', [channel, password])
		else:
			self.swapCurrentReceiver(receiver)

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
				self.logE("No default channel to part from: %s" % (e))
				return
		self.sendCmd('PART', channel, *message)

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
					return
			self.sendCmd('KICK', [channel, target], *reason)

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
		self.kick(target, channel, *reason)

	def quit(self, *message):
		""" Quit network. """
		self.sendCmd("QUIT", None, *message)

	def squit(self, server, *message):
		""" Tell server to disconnect server links"""
		self.sendCmd("SQUIT", server, *message)

	def message(self, target, *message):
		""" Message channel or user. """
		self.sendCmd("PRIVMSG", target, *message)

	def _message(self, *message):
		""" Message current channel or user. """
		try:
			target = self.getReceiver()
		except IRCError as e:
			self.logE("No default nick/channel to receive message: %s" % (e))
		else:
			self.message("PRIVMSG", target, *message)

	def action(self, target, *message):
		"""action command, does /me on specified channel"""
		self.message(target, "\x01ACTION %s\x01" % " ".join(message))

	def _action(self, *message):
		""" /me command defaults to current channel"""
		self._message("\x01ACTION %s\x01" % " ".join(message))

	def notice(self, target=None, *message):
		""" Notice channel or user. """
		try:
			target = self.getReceiver(target)
		except IRCError:
			message = list(message)
			message.insert(0, target)
			try:
				target = self.getReceiver()
			except IRCError as e:
				self.logE("No such nick/channel: %s" % (e))
				return
		self.sendCmd("NOTICE", target, *message)

	def userMode(self, mode):
		"""set mode on self"""
		self.sendCmd("MODE", [self.getNick(), mode])

	def mode(self, modeOrChannel, paramsOrMode="", params=""):
		"""
		set mode on self or channel
		Users should only rely on the mode actually being changed when 
		receiving an on_{channel,user}_mode_change callback.
		determine if modeOrChannel is channel
			if not a channel
				mode is modeOrChannel
		"""
		mode = paramsOrMode
		try:
			channel = self.getChannel(modeOrChannel)
		except IRCError as e:
			mode = modeOrChannel
			params = paramsOrMode
			try:
				channel = self.getChannel()
			except IRCError as e:
				self.logE("No default channel to set mode on: %s" % e)
				return
		self.sendCmd("MODE", [channel, mode, params])

	def topic(self, channel=None, *topic):
		"""
		Set topic on channel.
		Users should only rely on the topic actually being changed when 
		receiving an on_topic_change callback.
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
				return
		self.sendCmd('TOPIC', channel, *topic)

	def away(self, *message):
		""" Mark self as away. """
		self.sendCmd('AWAY', None, *message)

	def back(self):
		""" Mark self as not away. """
		self.away()

	def whois(self, target, serverMask=""):
		"""
		Return information about user.
		"""
		self.sendCmd('WHOIS', [target, serverMask])

	def whowas(self, target, *params):
		"""
		Return information about an offline user.
		"""
		self.sendCmd('WHOWAS', [target] + list(params))

	def admin(self, target=""):
		"""should return server's administrator information"""
		self.sendCmd('ADMIN', target)

	def cnotice(self, target, channel=None, *message):#TODO delete from mods
		pass

	def cprivmsg(self, target, channel = None, *message):
		"""send pm to target on channel"""
		try:
			target = self.getClient(target)
		except IRCError as e:
			self.logE("Client not found: %s" % (e))
			return
		try:
			channel = self.getChannel(channel)
		except IRCError:
			message = list(message)
			message.insert(0, channel)
			try:
				channel = self.getChannel()
			except IRCError as e:
				self.logE("No default Channel/Client: %s" % (e))
				return
		self.sendCmd('CPRIVMSG', [channel, target], *message)

	def die(self): # todo Mods
		"""shutdown the server"""
		self.sendCmd("DIE")

	def info(self, target=""):
		"""request help from server"""
		self.sendCmd("INFO", target)

	def invite(self, nickName, channel): #TODO add to mod
		"""invites nickName to channel"""
		self.sendCmd("INVITE", [nickname, channel])

	def ison(self, *nickNames):
		"""check nicknames in list are on network"""
		self.sendCmd("ISON", nickNames)

	def kill(self, target, *message):
		"""
		forcibly removes client from network
		only for use by IRC ops
		"""
		self.sendCmd("KILL", target, *message)

	def knock(self, channel, *message):#TODO mods
		"""notice to invite only channel with message"""
		self.sendCmd("KNOCK", channel, *message)

	def list(self, *channels):
		"""
		lists all channels on server
		if channels is given, returns channel topics
		"""
		self.sendCmd("LIST", ",".join(channels))

	def links(self, remoteServer="", serverMask=""):#TODO add to mods
		"""lists all servernames known by server"""
		self.sendCmd("LINKS", [remoteServer, serverMask])

	def lusers(self, mask="", target=""):
		"""gets stats about size of network"""
		self.sendCmd("LUSERS", [mask, target])

	def motd(self, server=""):
		"""returns message of the day"""
		self.sendCmd("MOTD", server)

	def names(self, *channels):
		"""returns list of who's on channels, or all users"""
		self.sendCmd("NAMES", ",".join(channels))

	def oper(self, target, password):
		"""authenticates user with password"""
		self.sendCmd("OPER", [target, password])

	def ping(self):
		"""pings server connection"""
		self.sendCmd("PING", self.getHost())

	def rehash(self):#TODO mods
		"""admin command to force reread of config"""
		self.sendCmd("REHASH")

	def restart(self):#TODO mods
		"""force server to restart itself"""
		self.sendCmd("RESTART")

	def rules(self):
		"""returns rules of the server"""
		self.sendCmd("RULES")

	def service(self, nickName, distribution, info):
		""" SERVICE command to register a new service."""
		self.sendCmd("SERVICE", [nickname, '*', distribution, '0', '0'], info)

	def servlist(self, mask="", type_=""):
		"""returns services on network"""
		self.sendCmd("SERVLIST", [mask, type_])

	def squery(self, service, *message):
		"""sends pm to service"""
		self.sendCmd("SQUERY", service, message)

	def setname(self, name):
		"""sets server's stored real name"""
		self.sendCmd("SETNAME", name)

	def silence(self, target = ""):
		"""
		prevents target from sending me messages
		if target not given, list all ignored targets
		prefix = [+, -]
		"""
		prefix = ""
		if target:
			try:
				target = self.getClient(target)
			except IRCError as e:
				self.logE("No default client found: %s" % e)
			else:
				if(target.silenced):
					prefix = '-'
				else:
					prefix = '+'
		self.sendCmd("SILENCE", "%s%s" % (prefix, target))

	def stats(self, query="", target=""):
		"""returns stats about the server"""
		self.sendCmd("STATS", [query, target])

	def summon(self, user, target="", channel=""):#TODO mods
		"""tells user on host to join"""
		self.sendCmd("SUMMON", [target, channel])


	def time(self, target=""):
		"""returns local time of the server"""
		self.sendCmd("TIME", target)

	def trace(self, target=""):#TODO add mods
		"""find the route to specific server and info about its peers"""
		self.sendCmd("TRACE", target)

	def uhnames(self):
		"""returns names in long format"""
		self.sendCmd("PROTOCTL UHNAMES")

	def userhost(self, target):
		"""returns list of info about nickname given"""
		try:
			target = self.getClient(target)
		except IRCError as e:
			self.logE("Client %s not found: %s" % (target, e))
		else:
			self.sendCmd("USERHOST", target)

	def userIP(self, target):
		"""returns direct IP of target"""
		try:
			target = self.getClient(target)
		except IRCError as e:
			self.logE("Could not find target: %s" % (e))
		else:
			self.sendCmd("USERIP", target)

	def users(self, target=""):
		"""returns list of users and info about them"""
		self.sendCmd("USERS", target)

	def userhost(self, *nickNames):#TODO mods
		"""returns list of info about each username"""
		self.sendCmd("USERHOST", list(nicknames))

	def version(self, target=""):
		"""returns version of server"""
		self.sendCmd("VERSION", target)

	def wallops(self, *message):
		"""sends message to all ops with mode w"""
		self.sendCmd("WALLOPS", None, *message)

	def who(self, target="", operator=False):
		"""returns list of users matching target"""
		o = ''
		if operator:
			o = 'o'
		self.sendCmd("WHO", [target, o])

	def connectServer(self, targetServer, port, remoteServer=""):#TODO add mods
		"""tells server to connect to another server"""
		self.sendCmd("CONNECT", [targetServer, port, remoteServer])



