
class Test():
	def __init__(self, callback):
		self.reply = callback  
		self.channel = None

	def COMMAND(self, sender, channel, cmd, message):
		if cmd == "test":
			if sender != channel:
				self.channel = channel
			self.reply("%s %s %s %s" % (sender, channel, cmd, message), channel)