"""
IRC connection class
Matthew Russell
last updated June 29, 2015

handles connecting, reconnecting, disconnecting, data I/O, and silently pings

"""
import socket
import time
import threading
import re

from IRCerrors import IRCIOError

PING = re.compile(r':?PING ?(.*)')

class IRCConnection():
	realName = "https://github.com/Clarvel/Py3bot"
	_reconnectTimeout = 300

	def __init__(self, host, port, nickCB, parseCB, password = None):
		self.host = host
		self.port = port
		self.password = password
		self._nickNameCallback = nickCB
		self._parseCallback = parseCB
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

		nickName = self._nickNameCallback()

		if(self.password):
			self.sendData("PASS %s" % (self.password))
		self.sendData("NICK %s" % nickName)
		self.sendData("USER %s %s * :%s" % (nickName, socket.gethostname(), 
			self.realName))

		self._listenEvent.clear()

		if not self._listenThread.isAlive():
			self._listenThread.start()

		if not self._parseThread.isAlive():
			self._parseThread.start()

		return "%s:%d" % (self.host, self.port)

	def disconnect(self, quitMessage = ""):
		if(self._connected):
			try:
				self.sendData("QUIT :%s" % (quitMessage))
			except Exception as e:
				pass
			self._connected = False
			self._connection.shutdown(socket.SHUT_RDWR)
			self._connection.close()
			self._buffer = ""
			self._listenEvent.set()

	def reconnect(self):
		self.disconnect()
		connectException = ""
		for timer in range(5, self._reconnectTimeout, 15):
			print("Reconnecting...")
			try:
				successVal = self.connect()
			except Exception as e:
				connectException = ": %s" % (e)
			else:
				return successVal
			time.sleep(timer)

		raise IRCIOError("Failed to reconnect after %d%s" % (timer/60, 
			connectException), self.host)

	def _listen(self):
		while self._connected:
			try:
				self._buffer = self._connection.recv(4096).decode('UTF-8')
			except IOError as e:
				print("G%s" % e.__name__)
				if self._connected:
					print("[IRC Connection]: Connection to host failed: %s. Retrying..." % (str(e)))
					try:
						self.reconnect()
					except Exception as e:
						print("[IRC Connection]: reconnect failed: %s" % e)
			else:
				self._listenEvent.set()

	def _parse(self):
		while self._listenEvent.wait() and self._connected:
			self._listenEvent.clear()
			lines = self._buffer.split("\n")
			self._buffer = lines.pop()
			for line in lines:
				line = line.rstrip("\r")

				test = PING.match(line)
				if(test):
					self.sendData("PONG %s" % (test.group(1)))
					#print("PONG %s" % (test.group(1)))
				else:
					self._parseCallback(line)

	def sendData(self, data):
		#print("SENDING: %s" % data)
		if self._connected:
			if not self._connection.send(bytes("%s\r\n" % (data), 'UTF-8')):
				#print(data)
				print("[IRCConnection]: Data send failed. Retrying...")
				try:
					self.reconnect()
				except Exception as e:
					print("[IRCCOnnection]: reconnect failed: %s" % e)
				else:
					self.sendData(data)

	def isConnected(self):
		"""returns true if server is connected"""
		return self._connected


if __name__ == '__main__':
	def nick():
		return "PYBOT"
	def parse(line):
		print(line)
	connect = IRCConnection("irc.darklordpotter.net", 6667, nick, parse)
	connect.connect()
	while(True):
		pass



