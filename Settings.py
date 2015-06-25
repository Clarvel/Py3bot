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
NICKS = ["Py3Bot", "Pybubbles", "PI", "PY", "PyBot"]
MODS = ["Dice", "Test", "CAH"]
ALERTCHAR = "@"
CHANNEL_PREFIXES = ['#', '&']
MESSAGE_LENGTH_LIMIT = 512
NICKNAME_LENGTH_LIMIT = 8
TOPIC_LENGTH_LIMIT = 450
NICKNAME_PREFIXES = ['@', '%', '+', '~'] # OP, halfOP, voice, channel owner
FORBIDDEN_CHARACTERS = { '\r', '\n', '\0' }
CHANNEL_SIGILS = {
	'PUBLIC' : "=",
	'PRIVATE' : "@",
	'SECRET' : "*"
}