#Py3bot
##IRC bot written in Python3
>Bot can be used as an IRC client through the terminal.
>Bot loads modes for each server instance

>Easily configurable settings

>run using: `python3 py3bot.py`

>**requires python 3.4 or later.**

>Bot loads the settings in settings.py on startup.

##TERMINAL COMMANDS:
In addition to all normal IRC commands, the following commands are also available in the terminal:
>`/quit(message?)`
>>terminates bot

>`/this` 
>>print current context in [server, channel] format

>`/server (host, port, terminalID?, password?)`

>`/s (host, port, terminalID?, password?)`
>>connects to specified server	

>`/swapServer (ID)`
>
>`/ss (ID)`
>>swap current server to server stored with the indicated ID	

>`/closeSever (ID, msg?)`
>>close specified server

>`/swapCurrentReceiver (ID)`
>>swaps current channel to channel stored with the indicated ID

>`/load (mod)`
>>loads specified mod in active context
  
>`/reload (mod)`
>>reloads specified mod in active context
  
>`/stop (mod)`
>>removes specified mod in active context
  
>`/modsList`
>>prints currently loaded mods in active context

#Mods
Mods are stored in the folder `mods/MODNAME/`. Once the server receives the command to load a specific mod, the file `MODNAME.py` in said folder is imported and the class `MODNAME` is instantiated. This class needs to inherit from the `IRCMod` class, imported from `IRCmod` to have access to the full range of possible command and reply options. A detailed list of these commands and replies are available in the file `IRCmod.py`

Mods are not inherently loaded on startup or upon connecting to a server unless the command to load the mods is added to the `ONLOGINCMDS` setting in `settings.py`

>A very basic default mod and a Dice mod are already included as examples.