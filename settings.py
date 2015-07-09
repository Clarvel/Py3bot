#https://en.wikipedia.org/wiki/Client-to-client_protocol
SERVERS = {
	"dlp" : {
		"HOST" : "irc.darklordpotter.net",
		"PORT" : 6667,
		"PASSWORD" : None,
		"ONLOGINCMDS" : [],
		"CHANNELS" : {
			"test" : {"NAME" : "#test", "PASSWORD" : ""}
		},
		"QUITMSG" : "Bye"
	},
}
NICKNAMES = ["Py3Bot", "Pybubbles", "PI", "PY", "PyBot"]
REAL_NAME = "https://github.com/Clarvel/Py3bot"
LOGIN_NAME = "Py3Bot"
ALERTCHAR = "@"
CHANNEL_PREFIXES = ['#', '&', '+', '!']
MESSAGE_LENGTH_LIMIT = 510
NICKNAME_PREFIXES = ['@', '%', '+', '~', '&'] # OP, halfOP, voice, channel owner, ???
#FORBIDDEN_CHARACTERS = { '\r', '\n', '\0' }
CHANNEL_SIGILS = {
	'PUBLIC' : "=",
	'PRIVATE' : "@",
	'SECRET' : "*"
}
AUTO_INVITE = True