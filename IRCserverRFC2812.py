"""
IRC server class
Matthew Russell
last updated June 25, 2015

implements the rfc 1459 protocol for IRC clients
https://tools.ietf.org/html/rfc2812

"""
import re
import time
import threading

from IRCerrors import IRCServerError
from IRCserverModable import IRCServerModable
from settings import NICKNAME_PREFIXES, ALERTCHAR, AUTO_INVITE
from IRCreceivers import IRCReceiver

class IRCServerRFC2812(IRCServerModable):
	_MESSAGE = re.compile(r'^:(\S+) (\S+)(?: ([^:]\S*))?(?: ([^:].*?))?(?: :(.+))?$') # (sender)(command)(recipient)(meta)(message)
	_USER = re.compile(r'(\S+)!(\S+)@(\S+)') # (nick)(loginNick)(IP)
	_ACTION = re.compile(r'^\x01ACTION (.*)\x01')

	def _parseInput(self, line):
		"""
		to parse input:
		first determine if the line is a server message
			assume the sender is the server
			determine if the sender is a client
				get the sender's client or make it
			get the recipient's client or make it
			try to execute the command
		"""
		#print(line)
		a = self._MESSAGE.match(line)
		if not a:
			self.logE("Input wasn't an IRC server message! [%s]" % (line))
			return

		sender = a.group(1)
		b = self._USER.match(a.group(1))
		if(b):
			try:
				sender = self.getReceiver(b.group(1))
			except Exception:
				sender = self._newReceiver(b.group(1))
			sender.loginName = b.group(2)
			sender.address = b.group(3)

		try:
			recipient = self.getRecipient(a.group(3))
		except Exception:
			#recipient is not a known channel/user/me, 
			#don't make a new one implicitly, could be a service
			recipient = a.group(3)

		command = a.group(2).lower()
		try:
			#args = a for a in [sender, recipient, a.group(4), a.group(5)] if a
			getattr(self, "_on_%s"%(command))(sender, recipient, a.group(4), a.group(5))
		except AttributeError:
			#assume command doesn't exist, use default
			self._onDefault(sender, recipient, command, meta, message)


	def _onDefault(self, sender, recipient, command, meta, message):
		self.log("%s -> %s [%s] %s :%s" % (sender, recipient, command, meta, message))


	## Callback handlers.

	def _on_error(self, sender, recipient, meta, message):
		""" Server encountered an error and will now close the connection. """
		self.logE("Received error: %s" % message)
		self.reconnect()
		self._callMods("onError", message)

	def _on_invite(self, sender, recipient, meta, message):
		""" INVITE command. """
		if(recipient.name == self.getNick()):
			self.log("%s invited you to %s" % (sender, message))
			if AUTO_INVITE:
				self.join(message)
		else:
			try:
				channel = self.getChannel(message)
			except Exception as e:
				self.logE("[INVITE]Could not find channel %s: %s" % (message, e))
			else:
				channel.log("%s invited %s to %s" % (sender, recipient, channel))
		self._callMods("onInvite", sender, recipient, message)

	def _on_join(self, sender, recipient, meta, message):
		""" JOIN command. """
		try:
			channel = self.getChannel(message)
		except Exception:
			channel = self._newReceiver(message)
		channel.log("%s joined %s" % (sender, channel))
		if sender.name == self.getNick():
			self.swapCurrentReceiver(channel.name)
		self._callMods("onJoin", sender, channel)

	def _on_kick(self, sender, recipient, meta, message):#TODO me checking
		""" KICK command. """
		self.log("%s kicked %s: %s" % (sender, recipient, message))
		self._callMods("onKick", sender, recipient, message)

	def _on_kill(self, sender, recipient, meta, message):#TODO
		""" KILL command. """
		self.log("Received kill: %s" % (message))
		self._callMods("onKill", message)

	def _on_mode(self, sender, recipient, meta, message):#TODO
		""" MODE command. """
		self.log("Set mode %s for %s on %s" % (message, recipient, sender))
		self._callMods("onMode", sender, recipient, message)

	def _on_nick(self, sender, recipient, meta, message):
		""" NICK command. """
		self.log("%s is now known as %s" % (sender, message))
		self._renameReceiver(sender.name, message)
		self._callMods("onNick", sender, message)

	def _on_notice(self, sender, recipient, meta, message):
		"""
		NOTICE command.
		if sender is the server, will be a string value and recipient will be 
		a service
		"""
		if(isinstance(recipient, IRCReceiver)):
			recipient.log("[NOTICE]%s: %s" % (sender, message))
		else:
			self.log("[NOTICE]: %s" % (message))
		self._callMods("onNotice", sender, recipient, message)

	def _on_part(self, sender, recipient, meta, message):
		""" PART command. """
		recipient.log("%s left: %s" % (sender, message))
		if sender.name == self.getNick():
			self.delReceiver(recipient.name)
		else:
			recipient.delUser(sender)
		self._callMods("onPart", sender, recipient, message)

	def _on_privmsg(self, sender, recipient, meta, message):
		""" PRIVMSG command. """
		if recipient.name == self.getNick():
			recipient = sender
		a = self._ACTION.match(message)
		if a:
			self._on_action(sender, recipient, meta, a.group(1))
		elif message.startswith(ALERTCHAR):
			try:
				cmd, msg = message.split(" ", 1)
			except ValueError:
				cmd = message
				msg = ""
			cmd = cmd.lstrip(ALERTCHAR)
			self._on_command(sender, recipient, cmd, msg)
		else:
			recipient.log("%s: %s" % (sender, message))
			self._callMods("onPrivmsg", sender, recipient, message)

	def _on_action(self, sender, recipient, meta, message):
		""" self._ACTION privmsg """
		recipient.log("*%s %s" % (sender, message))
		self._callMods("onAction", sender, recipient, message)

	def _on_command(self, sender, recipient, command, message):
		""" privmsg prefaced by command character"""
		recipient.log("%s: [%s] %s" % (sender, command, message))
		self._callMods("onCommand", sender, recipient, command, message)

	def _on_privnotice(self, sender, recipient, meta, message):
		""" PRIVNOTICE command. """
		recipient.log("[NOTICE]%s: %s" % (sender, message))
		self._callMods("privNotice", sender, recipient, message)

	def _on_quit(self, sender, recipient, meta, message):
		""" QUIT command. """
		self.log("%s quit: %s" % (sender, message))
		self._callMods("onQuit", sender, message)

	def _on_topic(self, sender, recipient, meta, message):
		""" TOPIC command. """
		recipient.log("Topic: %s %s" % (meta, message))
		self._callMods("onTopic", sender, recipient, meta)

	## Numeric responses.

	def _on_001(self, sender, recipient, meta, message):
		"""Welcome message."""
		self.log("%s" % message)
		self._welcomeEvent.set()
		self._callMods("on001", message)

	def _on_002(self, sender, recipient, meta, message):
		"""Server host."""
		self.log("%s" % message)
		self._callMods("on002", message)

	def _on_003(self, sender, recipient, meta, message):
		"""Server creation time."""	
		self.log("%s" % message)
		self._callMods("on003", message)

	def _on_004(self, sender, recipient, meta, message):
		""" Basic server information. """
		self.log("[INFO]: %s" % meta)
		self._callMods("on004", meta)

	def _on_005(self, sender, recipient, meta, message):
		"""supported limits"""
		#self.log("%s %s" % (meta, message))
		self._callMods("on005", " ".join([meta, message]))

	def _on_008(self, sender, recipient, meta, message):
		"""Server notice mask."""
		self.log("[SNOTICE]: %s" % message)
		self._callMods("on008", message)

	def _on_042(self, sender, recipient, meta, message):
		"""Unique client ID."""
		self.log("[CLIENT ID]: %s" % message)
		self._callMods("on042", message)

	def _on_250(self, sender, recipient, meta, message):
		"""Connection statistics."""
		self.log("[STATS]: %s" % message)
		self._callMods("on250", message)

	def _on_251(self, sender, recipient, meta, message):
		"""Amount of users online."""
		self.log("%s" % message)
		self._callMods("on251", message)

	def _on_252(self, sender, recipient, meta, message):
		"""Amount of operators online."""
		self.log("%s operators online" % (meta))
		self._callMods("on252", meta)

	def _on_253(self, sender, recipient, meta, message):
		"""Amount of unknown connections."""
		self.log("%s" % meta)
		self._callMods("on253", meta)

	def _on_254(self, sender, recipient, meta, message):
		"""Amount of channels."""
		self.log("%s channels" % (meta))
		self._callMods("on254", meta)

	def _on_255(self, sender, recipient, meta, message):
		"""Amount of local users and servers."""
		self.log("%s" % message)
		self._callMods("on255", message)

	def _on_265(self, sender, recipient, meta, message):
		"""Amount of local users."""
		self.log("%s" % message)
		self._callMods("on265", message)

	def _on_266(self, sender, recipient, meta, message):
		"""Amount of global users."""
		self.log("%s" % message)
		self._callMods("on266", message)

	def _on_301(self, sender, recipient, meta, message):
		""" User is away. """
		self.log("[AWAY]: %s" % message)
		self._callMods("on301", message)

	def _on_311(self, sender, recipient, meta, message):
		""" WHOIS user info. """
		self.log("[WHOIS]: %s" % message)
		self._callMods("on311", message)

	def _on_312(self, sender, recipient, meta, message):
		""" WHOIS server info. """
		self.log("[WHOIS SERVER]: %s" % message)
		self._callMods("on312", message)

	def _on_313(self, sender, recipient, meta, message):
		""" WHOIS operator info. """
		self.log("[WHOIS OP]: %s" % message)
		self._callMods("on313", message)

	def _on_314(self, sender, recipient, meta, message):
		""" WHOWAS user info. """
		self.log("[WHOWAS]: %s" % message)
		self._callMods("on314", message)

	def	on315(self, sender, recipient, meta, message):
		"""End of /WHO list."""
		self._callMods("on315")

	def _on_317(self, sender, recipient, meta, message):
		""" WHOIS idle time. """
		self.log("[WHOIS IDLE]: %s" % message)
		self._callMods("on317", message)

	def _on_318(self, sender, recipient, meta, message):
		""" End of /WHOIS list. """
		self._callMods("on318")

	def _on_319(self, sender, recipient, meta, message):
		""" WHOIS active channels. """
		self.log("[WHOIS CHANNELS]: %s" % message)
		self._callMods("on319", message)

	def _on_324(self, sender, recipient, meta, message):
		""" Channel mode. """
		self.log("[MODE: CHANNEL]: %s" % message)
		self._callMods("on324", message)

	def _on_329(self, sender, recipient, meta, message):
		""" Channel creation time. """
		self.log("%s" % message)
		self._callMods("on329", message)

	def _on_332(self, sender, recipient, meta, message):
		""" Current topic on channel join. """
		try:
			channel = self.getChannel(meta)
		except Exception as e:
			self.logE("[332]Could not find channel %s: %s" % (meta, e))
		else:
			channel.log("Topic: %s" % message)
			self._callMods("on332", channel, message)

	def _on_333(self, sender, recipient, meta, message):
		""" Topic setter and time on channel join. """
		params = meta.split()
		localTime = time.localtime(int(params[2]))
		t = time.strftime("%A, %d %B %Y, @ %I:%M:%S %p", localTime)
		try:
			channel = self.getChannel(params[0])
		except Exception as e:
			self.logE("[333]Could not find channel %s: %s" % (params[0], e))
		else:
			channel.log("Topic set by %s on %s" % (params[1], t))
		self._callMods("on333", channel, params[1], localTime)

	def _on_353(self, sender, recipient, meta, message):
		""" Response to /NAMES. """
		channelType, channelName = meta.split()
		clients = message.split()
		try:
			channel = self.getChannel(channelName)
		except Exception as e:
			self.logE("[353]Could not find channel %s: %s" % (channelName, e))
		else:
			channel.type = channelType

			for c in clients:
				prefix = ""
				if any(c.startswith(p) for p in NICKNAME_PREFIXES):
					prefix = c[0]
					c=c[1:]

				try:
					client = self.getClient(c)
				except Exception as e:
					client = self._newReceiver(c)
				else:
					channel.addUser(client, prefix)
					client.addChannel(channel)
			channel.log("Users: %s" % (message))
			self._callMods("on353", channel, message)

	def _on_366(self, sender, recipient, meta, message):
		"""End of /NAMES list."""
		self._callMods("on366")

	def _on_375(self, sender, recipient, meta, message):
		""" Start message of the day. """
		self.log("%s" % message)
		self._callMods("on375", message)

	def _on_372(self, sender, recipient, meta, message):
		""" Append message of the day. """
		self.log("%s" % message)
		self._callMods("on372", message)

	def _on_376(self, sender, recipient, meta, message):
		""" End of message of the day. """
		# MOTD is done, let's tell our bot the connection is ready.
		self._callMods("on376")

	def _on_401(self, sender, recipient, meta, message):
		""" No such nick/channel. """
		self.logE("[401]No such nick/channel: %s" % message)
		self._callMods("on401", message)

	def _on_402(self, sender, recipient, meta, message):
		""" No such server. """
		self.logE("[402]No such server: %s" % message)
		self._callMods("on402", message)

	def _on_412(self, sender, recipient, meta, message):
		""" no text to send. """
		self.logE("[412]%s" % (message))
		self._callMods("on412", message)

	def _on_422(self, sender, recipient, meta, message):
		""" MOTD is missing. """
		# MOTD is done, let's tell our bot the connection is ready.
		self.log("No MOTD")
		self._callMods("on422")

	def _on_421(self, sender, recipient, meta, message):
		""" Server responded with 'unknown command'. """
		self.logE('[421]Server responded with "Unknown command: %s"', message.params[0])
		self._callMods("on421", message)

	def _on_432(self, sender, recipient, meta, message):
		""" Erroneous nickname. """
		self.logE("[432]Erroneous nickname: %s" % message)
		self._callMods("on432", message)

	def _on_433(self, sender, recipient, meta, message):
		"""
		Nickname in use.
		if waiting for welcome, try a new nick
		"""
		self.logE("[433] %s" % message)
		if not self._welcomeEvent.isSet():
			self.nick(self.nickNames.next())
			self._renameReceiver(self._clientObject.name, self.nickNames.val())
		self._callMods("on433", message)

	def _on_436(self, sender, recipient, meta, message):
		"""Nickname collision, issued right before the server kills us."""
		self.logE("[436]Nickname Collision: %s" % message)
		self._callMods("on436", message)

	def _on_451(self, sender, recipient, meta, message):
		"""You have to register first."""
		self.logE("[451][%s]: %s" % (recipient, message))
		self._callMods("on451", recipient, message)

	def _on_462(self, sender, recipient, meta, message):
		"""You may not re-register."""
		self.logE("[462]You may not re-register. %s" % message)
		self._callMods("on462", message)

	def _on_482(self, sender, recipient, meta, message):
		""" you're not channel OP"""
		self.logE("[482]You're not channel OP. %s" % (message))
		self._callMods("on482", message)


