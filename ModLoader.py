"""
imports all mods indicated in IRCBot/settings.py and sets up an array of their names
Matthew Russell
Mar 2, 2015
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
				baseMod = __import__("mods.%s.%s" % (modName, modName), globals(), locals(), [modName], -1)
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
				reply = mod[command](sender, message)
			except Exception as e:
				#TODO: verify only mod[command] not existing
				pass
			else:
				return reply
		return "BAD COMMAND"


	def modsList(self): # return loaded mods list
		return self.loadedMods.keys()










