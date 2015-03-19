"""
Stored Regexes for the python IRC bot
Matthew Russell
Mar 2, 2015

IRC_CMDList
BotCMDList

"""

import re

PING = re.compile(r':?PING(.*)') # (response key) ping message


USER = re.compile(r':(\S+)!(\S+)@(\S+) (.+)') # user message (nick)(loginNick)(IP) (###)
#from group 4
PMSG = re.compile(r'PRIVMSG (\S+) :(.*)') # (chan|recp)(###|msg) private message
#from group(2)
ACTN = re.compile(r'.?ACTION (.*)') # (msg) action privmsg

JOIN = re.compile(r'JOIN :(\S+)') # (chan) user joined channel message
NICK = re.compile(r'NICK :(\S+)') # (newNick) user changed nickname
QUIT = re.compile(r'QUIT :(.*)') # (msg) user quit message
PART = re.compile(r'PART (\S+) ?:?(.*)') # (chan)(msg) user left channel
MODE = re.compile(r'MODE (\S+) (\S+) (\S+)') # (chan)(arg)(recp) set mode for person
NTCE = re.compile(r'NOTICE (\S+) :(\S+)') # (recp)(msg) notice message
INVT = re.compile(r'INVITE \S+ :(\S+)') # invite message (channel)


SERV = re.compile(r':((\S+\.\S+\.\S+)|(\S+)) (.+)') # server message (server)(###)
#from group 2
SNTC = re.compile(r'NOTICE AUTH :(.*)') # (msg) server notice
SMOD = re.compile(r'MODE \S+ :(.*)') # (msg) server mode set
NREP = re.compile(r'([0-9][0-9][0-9]) (.*)') # (number) (msg) numeric replies
#from group 2
SMSG = re.compile(r'\S+ :(.+)') # server message (msg)
OMSG = re.compile(r'\S+ ([0-9]+) :(.+)') # operators online message (ops)(message)
CMSG = re.compile(r'\S+ ([0-9]+) :(.+)') # channels formed message (chans)(message)
LMSG = re.compile(r'\S+ ([0-9]+) ([0-9]+) :(.+)') # local users (users)(max)(msg)
GMSG = re.compile(r'\S+ ([0-9]+) ([0-9]+) :(.+)') # global users (users)(max)(msg)
NAMS = re.compile(r'\S+ (@|=) (\S+) :(.+)') # names in channel ()(channel)(names)
ENNL = re.compile(r'\S+ (\S+) :(.+)') # end of names list (chan)(end of names list)
TMSG = re.compile(r'\S+ (\S+) :(.+)') # topic (channel)(msg)
CREA = re.compile(r'\S+ (\S+) (\S+) ([0-9]+)') # creator? (chan)(OP)(num)
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

