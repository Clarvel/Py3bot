"""
Dice mod:
supports mathematical expressions
use: @roll 4d6
"""
import random
import ast
import operator
import re

from IRCmod import IRCMod

BINOPS = {
	ast.Add: operator.add,
	ast.Sub: operator.sub,
	ast.Mult: operator.mul,
	ast.FloorDiv: operator.floordiv,
	ast.Div: operator.truediv,
	ast.Mod: operator.mod,
	ast.USub: operator.neg,
	ast.UAdd: operator.add
}

LARGENUM = 10000

class RollError(Exception):
	def __init__(self, string):
		self.string = string
	def __str__(self):
		return self.string
	def __repr__(self):
		return self.string


class Dice(IRCMod):
	# Dice settings
	ROLLTAG = re.compile(r'^([0-9\+\-\/\*\.\(\) de]+)(?: (.*))?$')
	ROLL = re.compile(r'([0-9]+d[0-9]+)')
	DICE = re.compile(r'([0-9]+)d([0-9]+)')
	MAXSIDES = 10000
	MINSIDES = 1
	MAXROLLS = 50
	MINROLLS = 1

	def onCommand(self, sender, channel, command, message):
		"""overload command function"""
		if command == 'roll' or command == 'solve':
			try:
				self.message(channel, "%s: %s" % (sender, 
					self._solve(message)))
			except Exception as e:
				self.message(channel, "%s, %s" % (sender, str(e)))
		elif command == 'limits':
			self.message(channel, self._limits())

	def _solve(self, string):
		msg = self.ROLLTAG.match(string)
		if not msg:
			raise RollError("yeah I can't do anything with that.")
		if msg.group(2):
			tag = " # %s" % msg.group(2)
		else:
			tag = ""
		matches = re.split(self.ROLL, msg.group(1).rstrip())
		equation = ""
		evalstr = ""
		for match in matches:
			val = match
			r = self.DICE.match(match)
			if r:
				rolls = self._roll(int(r.group(1)), int(r.group(2)))
				val = "[%s]" % '+'.join(str(a) for a in rolls)
				match = sum(rolls)
			equation += str(val)
			evalstr += str(match)
		try:
			evalstr = _eval(ast.parse(evalstr, mode='eval').body)
		except ZeroDivisionError as e:
			raise RollError("dude, don't divide by Zero.")
		except SyntaxError as e:
			raise RollError("give me a proper expression, scrub!")
		except TypeError as e:
			raise RollError("that's sure some odd Typing.")
		except KeyError as e:
			raise RollError("Despite what you may have heard, I don't do %s, sorry." % e)
		except RollError as e:
			raise
		except Exception as e:
			raise RollError("you made a %s! [%s]" % (type(e).__name__, e))
		return "%s=%s%s"%(equation, evalstr, tag)

	def _roll(self, r, f):
		total = []
		#verify they are inside the min and max int range
		if r >= self.MINROLLS and r <= self.MAXROLLS and f >= self.MINSIDES and f <= self.MAXSIDES:
			for i in range(self.MINROLLS, r+1):
				total.append(random.randint(self.MINSIDES, f))
			return total
		else:
			raise RollError(self._limits())

	def _limits(self):
		return "numbers must be in: [%s:%s]d[%s:%s]" % (self.MINROLLS, 
			self.MAXROLLS, self.MINSIDES, self.MAXSIDES)

def _eval(node):
	if isinstance(node, ast.Expression):
		return _eval(node.body)
	elif isinstance(node, ast.Str):
		return node.s
	elif isinstance(node, ast.Num):
		if node.n > LARGENUM or node.n < -LARGENUM:
			raise RollError("yeah, no, I don't deal with numbers larger than %d" % LARGENUM)
		return node.n
	elif isinstance(node, ast.BinOp):
		return BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
	elif isinstance(node, ast.UnaryOp):
		return BINOPS[type(node.op)](_eval(node.operand))
	elif isinstance(node, ast.Name):
		raise RollError("Unsupported variable name")
	elif isinstance(node, ast.Call):
		raise RollError("expressions only dude, wtf")
	else:
		raise RollError('Unsupported type {}.'.format(node))




