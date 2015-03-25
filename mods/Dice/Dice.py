import random

class Dice():
	def __init__(self, callback):
		self.reply = callback
		# Dice settings
		self.MAXSIDES = 10000
		self.MINSIDES = 1
		self.MAXROLLS = 50
		self.MINROLLS = 1

	def COMMAND(self, sender, channel, cmd, message):
		if cmd == "roll":
			a=self.roll(sender, message)
			self.reply(a, channel)
		elif cmd == "help.Dice":
			self.reply(self.limits(), channel)


	def roll(self, sender, string):
		#try to split for integers
		try:
			numbs = string.split('d')
		except:
			return "Invalid input: " + string
		#verify numbers are integers
		try:
			numbs[0] = int(numbs[0])
		except ValueError:
			return "invalid number of dice"
		except AttributeError:
			return "Invalid input: ", string
		try:
			numbs[1] = int(numbs[1])
		except ValueError:
			return "invalid number of faces"
		except AttributeError:
			return "Invalid input: ", string
		#verify they are inside the min and max int range
		if (numbs[0] >= self.MINROLLS and numbs[0] <= self.MAXROLLS) and (numbs[1] >= self.MINSIDES and numbs[1] <= self.MAXSIDES):
			reply = sender + " rolled: [" + str(random.randint(1, numbs[1]))
			for i in range(1, numbs[0]):
				reply = reply + ", " + str(random.randint(1, numbs[1]))
			#reply with randomized integers
			return reply + "]"
		else:
			return self.limits()

	def limits(self):
		return "Numbers must be between: (" + str(self.MINROLLS) + ":" + str(self.MAXROLLS) + ") d (" + str(self.MINSIDES) + ":" + str(self.MAXSIDES) + ")"
