"""
imports all mods indicated in IRCBot/settings.py and sets up an array of their names
Matthew Russell
Apr 19, 2014

"""
#system imports
import sys, importlib

#IRCbot settings import, for activated mods list
import settings

class ModLoader():
	def __init__(self):
		self.loadMods()

	#load all mods listed in IRCBot/settings.py
	def loadMods(self):
		self.loadedMods = []
		self.basiccmds = []
		self.nickcmds  = []
		self.msgscmds  = []
		for modName in settings.MODS:
			#make path name
			path = "mods." + modName + "."
			try:
				# from mods.Default.Default import Default
				baseMod = __import__(path + modName, globals(), locals(), [modName], -1)
			except ImportError as error:
				print("Import of mod '%s' failed: %s" % (modName, error))
			else:
				try:
					baseModSettings = __import__(path + "settings", globals(), locals(), [settings], -1)
				except ImportError as error:
					print("Import of mod '%s's settings.py failed: %s" % (modName, error))
				else:
					mod = getattr(baseMod, modName)()
					self.loadedMods.append(mod)
					index = len(self.loadedMods) - 1
					#import command into one of the lists with an integer indexing the mod
					try:
						for command in baseModSettings.COMMANDS:
							temp = [command, index]
							self.basiccmds.append(temp)
					except AttributeError as error:
						print(error)
						pass
					try:
						for command in baseModSettings.NICKCMDS:
							temp = [command, index]
							self.nickcmds.append(temp)
					except AttributeError as error:
						print(error)
						pass
					try:
						for command in baseModSettings.ALLMSGS:
							temp = [command, index]
							self.msgscmds.append(temp)
					except AttributeError as error:
						print(error)
						pass
		string = "Loaded mods: "
		for mod in self.loadedMods:
			string = string + "[" + mod.__class__.__name__ + "] "
		print string

	#finds the mod the command originated form, returns the run command
	def callMod(self, sender, MSG, command):
		#search through the mods to find the relevant command, if found return that string
		"""
		could use work, rather ugly
		"""
		if command == "@n":
			for listcmd in self.nickcmds:
				mod = self.loadedMods[listcmd[1]] 
				# try running the command and return
				try:
					print "From [", mod.__class__.__name__, "] excecuting [", command, "] on message [", MSG, "]"
					temp = getattr(mod, listcmd[0])(sender, MSG)
				except AttributeError as error:
					print "Mod function error: %s" % (error)
				else:
					return temp
		elif command == "@a":
			for listcmd in self.msgscmds:
				mod = self.loadedMods[listcmd[1]] 
				# try running the command and return
				try:
					print "From Mod: [", mod.__class__.__name__, "] excecuting: [", command, "] on message: [", MSG, "]"
					temp = getattr(mod, listcmd[0])(sender, MSG)
				except AttributeError as error:
					print "Mod function error: %s" % (error)
				else:
					return temp
		else:
			for listcmd in self.basiccmds:
				if listcmd[0] == command:
					# mod found
					mod = self.loadedMods[listcmd[1]] 
					# try running the command and return
					try:
						print "From Mod: [", mod.__class__.__name__, "] excecuting: [", command, "] on message: [", MSG, "]"
						temp = getattr(mod, listcmd[0])(sender, MSG)
					except AttributeError as error:
						print "Mod function error: %s" % (error)
					else:
						return temp
	# list mods loaded into PyRCbot
	def listMods(self):
		string = ""
		for mod in loadedMods:
			string = string +  "[" + mod.__class__.__name__ + "] "
		return string










