"""
Stored Regexes for the python IRC bot
Matthew Russell
Feb 22, 2015

IRC_CMDList
BotCMDList

"""

import re

class RegexCompiler():
	def __init__(self):
		self.alertChar = alertChar

	def replyRegexes():
		self.PING = re.compile(r':?PING(.*)')

	def termRegexes():
		tAlert = '/'
		# normal server interactions that should be interrupted
		self.JOIN = re.compile(r"%sjoin (*)" % (tAlert))
		self.QUIT = re.compile(r"%squit (*)" % (tAlert))
		self.EXIT = re.compile(r"%sexit (*)" % (tAlert))
		# else use this for tAlert prefix
		self.SERVCMD = re.compile(r"^%s([a-zA-Z]+) (*)" % (tAlert))

	def botRegexes(alertChar):
		# bot alert prefix
		self.BOTCMD = re.compile(r"%s*" % (alertChar))
		self.BOTALRT = 0

class REMatch(object):
    """
    Easily test against multiple regex patterns.
    Ref: http://stackoverflow.com/questions/2554185/match-groups-in-python
    """
    def __init__(self, string):
        self.string = string

    def match(self, regex):
        self.re_match = regex.match(self.string)
        return bool(self.re_match)

    def group(self, i):
        return self.re_match.group(i)

    def groups(self):
        return self.re_match.groups()