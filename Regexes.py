"""
Stored Regexes for the python IRC bot
Matthew Russell
Mar 2, 2015

IRC_CMDList
BotCMDList

"""

import re

PING = re.compile(r':?PING(.*)') # (response key) # ping message
PMSG = re.compile(r':(.*)!(.*@.*) (.*) (.*) :(.*)') # (sender)(IP)(PRIVMSG)(channel or ME)(message) # private message

ACTN = re.compile(r'.?ACTION (.*)') # (message) # action privmsg

SMSG = re.compile(r':.* [0-9]+ (.*) :(.*)') # (OPTIONS)(message) # server message

SJON = re.compile(r'JOIN') # if server join message
SPRM = re.compile(r'(.*) (.*)') # if server PM  (ME) (OPTIONS)

SMAT = re.compile(r'@ (#.*)') # if names list  (channel)
SMCH = re.compile(r'(#.*)') # channel


NTCE = re.compile(r':.* NOTICE (.*):(.*)')
MODE = re.compile(r':(.*) MODE (.*) :(.*)') # (ME) (ME) (message)
JOIN = re.compile(r':(.*)!(.*@.*) JOIN :(.*)') # (ME) (IP) (message) # channel join message
QUIT = re.compile(r':(.*)!(.*@.*) QUIT :(.*)') # (name) (IP) (message)


#MSG_PAT = re.compile(r':?.* (.*) :(.*)')
#self.logger.log("[%s %s] %s" % (self.host, msg.group(1), msg.group(2)))


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

        