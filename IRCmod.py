"""
overloadable irc mod class
matthew russell
june 24, 2015
"""
class IRCMod:
	def __init__(self, server):
		self.__server = server # server callback function
	
	# callable functions

	def nick(self, name):
		self.__server.nick(name)
	def join(self, channel, password=""):
		self.__server.join(channel, password)	
	def part(self, channel, message=""):
		self.__server.part(channel, message)
	def kick(self, target, channel, reason=""):
		self.__server.kick(target, channel, reason)
	def ban(self, target, channel, range=0):
		self.__server.ban(target, channel, range)
	def unban(self, target, channel, range=0):
		self.__server.unban(target, channel, range)
	def kickban(self, target, channel, reason="", range=0):
		self.__server.kickban(target, channel, reason, range)
	def quit(self, message=""):
		self.__server.quit(message)
	def message(self, target, message):
		self.__server.message(target, message)
	def action(self, target, message): # TODO
		self.__server.action(target, message)
	def notice(self, target, message):
		self.__server.notice(target, message)
	def mode(self, mode, target, channel):
		self.__server.mode(mode, target, channel)
	def topic(self, channel, topic=""):
		self.__server.topic(channel, topic)
	def away(self, message=""):
		self.__server.away(message)
	def back(self):
		self.__server.back()
	def whois(self, target):
		self.__server.whois(target)
	def whowas(self, target):
		self.__server.whowas(target)
	def admin(self):
		self.__server.admin()
	def cnotice(self, target, channel, message):
		self.__server.cnotice(target, channel, message)
	def cprivmsg(self, target, channel, message):
		self.__server.cprivmsg(target, channel, message)
	def help(self):
		self.__server.help()
	def info(self):
		self.__server.info()
	def ison(self, message):
		self.__server.ison(message)
	def kill(self, target, message):
		self.__server.kill(target, message)
	def knock(self, channel, message):
		self.__server.knock(channel, message)
	def list(self, *channels):
		self.__server.list(channels)
	def motd(self):
		self.__server.motd()
	def names(self, *channels):
		self.__server.names(channels)
	def oper(self, target, password):
		self.__server.oper(target, password)
	def ping(self):
		self.__server.ping()
	def rules(self):
		self.__server.rules()
	def servlist(self):
		self.__server.servlist()
	def squery(self, service, message):
		self.__server.squery(service, message)
	def setname(self, name):
		self.__server.setname(name)
	def silence(self, target=""):
		self.__server.silence(target)
	def stats(self):
		self.__server.stats()
	def time(self):
		self.__server.time()
	def uhnames(self):
		self.__server.uhnames()
	def userhost(self, target):
		self.__server.userhost(target)
	def userIP(self, target):
		self.__server.userIP(target)
	def users(self):
		self.__server.users()
	def version(self):
		self.__server.version()
	def wallops(self, message):
		self.__server.wallops(message)
	def whop(self, target):
		self.__server.whop(target)
	def who(self, target):
		self.__server.who(target)

	# overloadable functions

	def onError(self, message):
		pass
	def onInvite(self, sender, recipient, message):
		pass
	def onJoin(self, sender, channel):
		pass
	def onKick(self, sender, recipient, message):
		pass
	def onKill(self, message):
		pass
	def onMode(self, sender, recipient, message):
		pass
	def onNick(self, sender, newNick):
		pass
	def onNotice(self, sender, recipient, message):
		pass
	def onPart(self, sender, recipient, message):
		pass
	def onPrivmsg(self, sender, recipient, message):
		pass
	def onAction(self, sender, recipient, message):
		pass
	def onCommand(self, sender, recipient, command, message):
		pass
	def onPrivnotice(self, sender, recipient, message):
		pass
	def onQuit(self, sender, message):
		pass
	def onTopic(self, sender, recipient, message):
		pass
	def on001(self, message):
		pass
	def on002(self, message):
		pass
	def on003(self, message):
		pass
	def on004(self, message):
		pass
	def on005(self, message):
		pass
	def on008(self, message):
		pass
	def on042(self, message):
		pass
	def on250(self, message):
		pass
	def on251(self, message):
		pass
	def on252(self, message):
		pass
	def on253(self, message):
		pass
	def on254(self, message):
		pass
	def on255(self, message):
		pass
	def on265(self, message):
		pass
	def on266(self, message):
		pass
	def on301(self, message):
		pass
	def on311(self, message):
		pass
	def on312(self, message):
		pass
	def on313(self, message):
		pass
	def on314(self, message):
		pass
	def on315(self):
		pass
	def on317(self, message):
		pass
	def on318(self):
		pass
	def on319(self, message):
		pass
	def on324(self, message):
		pass
	def on329(self, message):
		pass
	def on332(self, channel, message):
		pass
	def on333(self, channel, setter, time):
		pass
	def on353(self, channel, message):
		pass
	def on366(self):
		pass
	def on375(self, message):
		pass
	def on372(self, message):
		pass
	def on376(self):
		pass
	def on401(self, message):
		pass
	def on402(self, message):
		pass
	def on412(self, message):
		pass
	def on422(self):
		pass
	def on421(self, message):
		pass
	def on432(self, message):
		pass
	def on433(self, message):
		pass
	def on436(self, message):
		pass
	def on451(self, command, message):
		pass
	def on462(self, message):
		pass
	def on482(self, message):
		pass