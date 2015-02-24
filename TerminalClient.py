"""
Terminal Client Thread class
by Matthew Russell
last updated Feb 21, 2015

class spawns off a thread to receive user input while not impeding other processes
user input is sent to the given callback function to be handled elsewhere
no need to explicitly kill thread, daemon ensures it will die one main program exit.

"""

import threading

class TerminalClient():
	def __init__(self, callback):
		self.callback = callback
		self.thread = threading.Thread(target=self.userInput) # spawn thread
		self.thread.daemon = True # ensure thread dies when main thread dies
		self.thread.start() # start thread

	def userInput(): # waits for input, writes it to callback function
		while(True):
			self.callback(input(""))