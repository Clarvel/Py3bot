"""
Logger handles saving messages to the logs and writing to terminal

Matthew Russell
Feb 22 2015
"""
#system import
import time, os

class Logger:

    def __init__(self, filename):
    	self.path = os.path.join(os.path.dirname(__file__), "logs/%s.txt" % (filename))

    def write(self, message):
        #Write a message to the file.
        #open file in append mode
        fileObj = open(self.path, "a")
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        fileObj.write("%s %s\n" % (timestamp, message))
        fileObj.flush()
        fileObj.close()
        #Write a message to the terminal
        print("%s %s" % (timestamp, message))

    def error(self, message):
        self.write("[ERROR] " + message)
    def info(self, message):
        self.write("[INFO] " + message)
    def log(self, message):
        self.write(message)