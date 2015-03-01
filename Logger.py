"""
Logger handles saving messages to the logs and writing to terminal

Matthew Russell
Feb 22 2015
"""
#system import
import time, os, errno

class Logger:

	def __init__(self, filename):
		self.path = os.path.join(os.path.dirname(__file__), "logs/%s" % (filename))
		try:
			folders = filename.split("/")
			folders.pop()
			folderPath = os.path.join(os.path.dirname(__file__), "logs/%s" % ("/".join(folders)))
			os.makedirs(folderPath)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise

	def write(self, message):
		#Write a message to the file.
		timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
		#open file in append mode
		try:
			fileObj = open(self.path + ".txt", "a+")
		except Exception as e:
			print("[ERROR] Could not write to file: %s" % e)
		else:
			fileObj.write("%s%s\n" % (timestamp, message))
			fileObj.flush()
			fileObj.close()
		#Write a message to the terminal
		print("%s%s" % (timestamp, message))

	def error(self, message):
		self.write("[ERROR] " + message)
	def info(self, message):
		self.write("[INFO] " + message)
	def log(self, message):
		self.write(message)