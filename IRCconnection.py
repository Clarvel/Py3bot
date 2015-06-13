
import socket
import time
import threading
import re

from IRCerror import IRCError

PING = re.compile(r':?PING(.*)')

class IRCConnection():
	def __init__(self, host, port, nickCB, parseCB, password = None):
		self.host = host
		self.port = port
		self.password = password
		self.quitMessage = ""
		self._nickNameCallback = nickCB
		self._parseCallback = parseCB
		self._buffer = ""
		self._connectTimeout = 30
		self._reconnectTimeout = 300
		self._connected = False
		self._pinged = False

		self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def connect(self):
		self._connection.connect((self.host, self.port))
		self._connected = True

		nickName = self._nickNameCallback()

		if(self.password):
			self.sendData("PASS %s" % (self.password))
		self.sendData("USER %s %s * :%s" % (nickName, socket.gethostname(), 
			nickName))
		self.sendData("NICK %s" % nickName)

		listenThread = threading.Thread(target=self.listen)
		listenThread.daemon = True # ensure thread dies when main dies
		listenThread.start()

		# wait for ping before continuing, otherwise timeout and fail
		timer = 0
		while not self._pinged:
			timer += 1
			time.sleep(1)
			if timer >= self._connectTimeout:
				self.disconnect()
				raise IRCError("Connection to host %s failed: Did not receive ping after %is" % (self.host, timer))

	def disconnect(self):
		if(self._connected):
			self.sendData("QUIT %s" % (self.quitMessage))
			self._connection.shutdown(socket.SHUT_RDWR)
			self._connection.close()
			self._buffer = ""
			self._connected = False
			self._pinged = False

	def reconnect(self):
		self.disconnect()
		timer = 0
		while(timer < self._reconnectTimeout):
			timer += 30
			time.sleep(timer)
			try:
				self.connect()
			except Exception as e:
				pass
			else:
				return
		raise IRCError("Failed to reconnect after %ds" % (timer/60))

	def listen(self):
		while self._connected:
			try:
				self._buffer += self._connection.recv(4096).decode('UTF-8')
			except IOError as e:
				self.reconnect()
				print("[ERROR]: Connection to host failed: %s" % (str(e)))
			else:
				lines = self._buffer.split("\n")
				self._buffer = lines.pop()
				for line in lines:
					line = line.rstrip("\r")

					test = PING.match(line)
					if(bool(test)):
						self.sendData("PONG %s" % (test.group(0)))
						self._pinged = True
					else:
						parseThread = threading.Thread(
							target=self._parseCallback, args=(line,))
						parseThread.daemon = True
						parseThread.start()

	def sendData(self, data):
		if not self._connection.send(bytes("%s\r\n" % (data), 'UTF-8')):
			self.disconnect()
			raise IRCError("Socket Connection Broken")



if __name__ == '__main__':
	def nick():
		return "PYBOT"
	def parse(line):
		print(line)
	connect = IRCConnection("irc.darklordpotter.net", 6667, nick, parse)
	connect.connect()
	while(True):
		pass



