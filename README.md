# Py3bot
IRC bot written for Python3
Bot can be used as an IRC client throguh the terminal.
Bot dynamically loads mods for each channel its in
Easily configurable settings
Comes pre-packeaged with a Dice mod

run using "python3 __init__.py"
requires python 3.3.2 or later.
Bot loads the settings in Settings.py on startup.

TERMINAL COMMANDS:
/quit
	terminates bot

/this
	print current context in [server, channel] format


/server (host, port, ID?, password?)
/s (host, port, ID?, password?)
	connects to specified server
	
/setSe (ID)
/ss (ID)
	swap current server to server stored with the indicated ID
	
/close (ID, msg?)
	close specified server

/join (name, ID?, password?)
/c (name, ID?, password?)
	connects to specified channel

/setCh (ID)
/sc (ID)
	swaps current channel to channel stored with the indicated ID
	
/part (ID)
	close specified channel


/oper (name, password)
	request operator privleges
	
/mode (OP, name, msg?)
	where OP = ((+|-)|o|p|s|i|t|n|b|v|w|m|l|k)
	change user modes

/topic (msg?)
	sets topic for channel
	if topic not given, prints the current topic
	
/names 
	lists all nicknames for specified channel
	
/nick (newName)
	changes the bot's nickname to the given nickname
	
/list
	lists channels and topics
	
/invite (name, channel?)
	invite a user to a channel
	if channel not specified, invites to active channel
	
/kick (name, reason?)
	removes person from channel


/pm (name, msg)
	send message to person
	
/notice (name, msg)
	send message to person

/whois (name)
	get info on name
	
/whowas (name)
	get info on name

/kill (name, msg?)
	disconnect someone's ghost
	
	
/load (mod)
  loads specified mod in active context
  
/reload (mod)
  reloads specified mod in active context
  
/stop (mod)
  removes specified mod in active context
  
/loaded
/mods
  prints currently loaded mods in active context
  
  
  
MODS:
mods are initialized per channel, and take the following format:
in /mods/MODNAME/MODNAME.py:

class MODNAME():
  def __init__(self, callback):
    self.reply = callback
  def COMMAND(self, sender, channel, cmd, message):
    # command was given, this should do nothing if cmd does not match any recognized commands for this mod
    if cmd == "cmdReply":
      self.reply("Replying to command here", channel)
  def MENTION(self, sender, channel, message):
    # the bot was mentioned by name, this should do nothing if cmd does not match any recognized commands for this mod
    pass

You do not have to include COMMAND or MENTION if not used for your mod.
Replace MODNAME with the name of your module.
callbacks require two inputs, the message and the recipient. The recipient can be a channel or a user of the server. 


ADMIN:
NOTE: enabling this is NOT SAFE in any way, leaving ADMIN_PASSWORD as None will disable this
ENABLE AT OWN RISK

In settings.py, you may set an admin password in the ADMIN_PASSWORD field.
This setting will, once set and the bot is running will allow you to PM the bot with "ADMIN PASS" where PASS is the password setup beforehand.
Once set, the bot will execute any terminal commands at the server level you and only you give it.(/join and below in the list above)
It tracks Admin privleges by IP, and currently doesn't revoke privleges on disconnect, so be aware of this when your connection is spotty.
