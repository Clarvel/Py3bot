"""
imports all mods indicated in IRCBot/settings.py and sets up an array of their names
Matthew Russell
Mar 18, 2015
"""
#system imports
import sys, importlib

class ModLoader():
	def __init__(self):
		self.loadedMods = {}
		pass

	def load(self, modsList):
		for modName in modsList:
			#make path name
			try:
				# from mods.Default.Default import Default
				baseMod = importlib.import_module("mods.%s.%s" % (modName, modName))
				print(baseMod)
				#baseMod = __import__("mods.%s.%s" % (modName, modName), globals(), locals(), [modName], -1)
			except ImportError as error:
				print("Import of mod '%s' failed: %s" % (modName, error))
			else:
				self.loadedMods[modName] = baseMod
		print("Loaded mods: [%s]" % (", ".join(self.loadedMods.keys())))

	#finds the mod the command originated form, returns the run command
	def callMod(self, sender, command, message):
		#search through the mods to find the relevant command, if found return that string
		for mod in self.loadedMods:
			try:
				reply = getattr(mod, command)(sender, message)
			except AttributeError as e:
				#command didn't exist for this mod, ignore error
				pass
			else:
				return reply
		return "Command [%s] not found!" % (command)


	def modsList(self): # return loaded mods list
		return self.loadedMods.keys()

class default():
	def __init__(self):
		pass








