class Default():
	def __init__(self, callback):
		self.reply = callback
		pass
	def COMMAND(self, sender, channel, cmd, message):
		self.reply("Sorry, I didn't understand that, %s" % sender, channel)
	def MENTION(self, sender, channel, message):
		self.reply("acknowlwged, %s" % sender, channel)