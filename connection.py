"""
Connection class
Matthew Russell
last updated June 29, 2015

handles connecting, reconnecting, disconnecting, data I/O, and silently pings

"""
import socket
import time
import threading
import re


class Connection():
	"""
	class handles connection to some host/port, writing and listening to said
	uses 2 threads, one to listen to the connection and one to parse strings
	send should raise IOError if connection fails
	"""
	PING = re.compile(r':?PING ?(.*)')

	def __init__(self, host, port, parseCallback):
		self.host = host
		self.port = port
		self._parseCallback = parseCallback
		self._buffer = ""
		self._connected = False
		self._connection = None

		self._listenThread = threading.Thread(target=self._listen)
		self._listenThread.daemon = True # ensure thread dies when main dies

		self._parseThread = threading.Thread(target=self._parse)
		self._parseThread.daemon = True

		self._listenEvent = threading.Event()

	def connect(self):
		self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._connection.connect((self.host, self.port))
		self._connected = True

		self._listenEvent.clear()

		if not self._listenThread.isAlive():
			self._listenThread.start()

		if not self._parseThread.isAlive():
			self._parseThread.start()

		return "%s:%d" % (self.host, self.port)

	def disconnect(self):
		self._connected = False
		self._connection.shutdown(socket.SHUT_RDWR)
		self._connection.close()
		self._buffer = ""
		self._listenEvent.set()

	def _listen(self):
		while self._connected:
			try:
				self._buffer = self._connection.recv(4096).decode('UTF-8')
			except IOError as e:
				if self._connected:
					print("CONNECTION: Listener failed, retrying connection")
					self.disconnect()
					self.connect()
			else:
				self._listenEvent.set()

	def _parse(self):
		while self._listenEvent.wait() and self._connected:
			self._listenEvent.clear()
			lines = self._buffer.split("\n")
			self._buffer = lines.pop()
			for line in lines:
				line = line.rstrip("\r")
				pongTest = self.PING.match(line)
				if(pongTest):
					self.send("PONG %s" % (pongTest.group(1)))
					#print("PONG %s" % (pongTest.group(1)))
				else:
					self._parseCallback(line)

	def send(self, data):
		#print("SENDING: %s" % data)
		if self._connected:
			if not self._connection.send(bytes("%s\r\n" % (data), 'UTF-8')):
				raise IRCIOError("Output failed")

	def isConnected(self):
		"""returns true if server is connected"""
		return self._connected


if __name__ == '__main__':
	def parse(line):
		print(line)
	connect = Connection("irc.darklordpotter.net", 6667, parse)
	connect.connect()
	connect.send("NICK A")
	connect.send("USER B C * :D")
	while(True):
		pass



