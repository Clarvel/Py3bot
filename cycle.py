"""
Matthew Russell
July 9 2015

circular list class with methods next, prev, val, get
"""
class Cycle():
	def __init__(self, list_):
		self.list = list_
		self.index = 0

	def next(self):
		self.index += 1
		return self.val()
	def prev(self):
		self.index -= 1
		return self.val()
	def val(self):
		return self.list[self.index % len(self.list)]
	def get(self, index):
		return self.list[index % len(self.list)]