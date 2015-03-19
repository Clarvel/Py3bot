"""
imports all mods indicated in IRCBot/settings.py and sets up an array of their names
Matthew Russell
Mar 18, 2015
"""
#system imports
import sys
import importlib

class ModLoader():
	def __init__(self, channel, callback):
		self.channel = channel
		self.callback = callback
		self.loadedMods = {}
		pass

	def load(self, modsList):
		returnStr = ""
		for modName in modsList:
			#make path name
			try:
				# from mods.Default.Default import Default
				sys.path.append("%s/mods/%s/%s" % (sys.path[0], modName, modName))
				baseMod = importlib.import_module("mods.%s.%s" % (modName, modName))
				#print(baseMod)
				mod = getattr(baseMod, modName)(self.callback)
				#print(mod)
			except ImportError as error:
				returnStr += ("[ERROR] Import of mod '%s' failed: %s\n" % (modName, error))
			else:
				self.loadedMods[modName] = [baseMod, mod]
		return returnStr + ("Loaded mods: [%s]" % (", ".join(self.loadedMods.keys())))

	def reload(self, modName=None):
		if modName != None:
			modNames = [modName]
		else:
			modNames = self.loadedMods.keys()

		returnStr = ""
		for key in modNames:
			try:
				baseMod = importlib.reload(self.loadedMods[key][0])
				mod = getattr(baseMod, key)(self.callback)
			except Exception as e:
				returnStr += "%s\n" % e
			else:
				self.loadedMods[key] = [baseMod, mod]
		return returnStr + "Reloaded [%s]" % (", ".join(modNames))
	
	def stop(self, modName): # removes mods from active list, will have to be loaded again
		if modName != None:
			modNames = [modName]
		else:
			modNames = self.loadedMods.keys()
		for key in modNames:
			del self.loadedMods[key]
		return "Stopped [%s]" % (", ".join(modNames))

	def callMod(self, sender, command, message): #finds the mod the command originated form, returns the run command
		#search through the mods to find the relevant command, if found return that string
		for mod in self.loadedMods.keys():
			try:
				reply = getattr(self.loadedMods[mod][1], "COMMAND")(sender, self.channel, command, message)
			except Exception as e:
				print(e)
				#command didn't exist for this mod, ignore error
			else:
				return reply
		return "Command [%s] not found!" % (command)

	def mentMod(self, sender, message): # bot was mentioned in a message
		#search through the mods to find the relevant command, if found return that string
		for mod in self.loadedMods.keys():
			try:
				reply = getattr(self.loadedMods[mod][1], "MENTION")(sender, self.channel, message)
			except Exception as e:
				print(e)
				#command didn't exist for this mod, ignore error
			else:
				return reply

	def modsList(self): # return loaded mods list
		return "Loaded mods: %s" % list(self.loadedMods.keys())









