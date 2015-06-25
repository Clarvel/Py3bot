"""
imports all mods indicated in IRCBot/settings.py and sets up an array of their names
Matthew Russell
june 25, 2015
"""
#system imports
import sys
import importlib

from IRCserverCommands import IRCServerCommands
from IRCerrors import IRCModError

class IRCServerModable(IRCServerCommands):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._loadedMods = {}

	def load(self, *modsList):
		"""
		trys to load all mods in given list 
		fails gracefully, prints status string of mods
		"""
		for modName in modsList:
			try:
				# example call: from mods.Default.Default import Default
				baseMod = importlib.import_module("mods.%s.mod" % (modName))
				#sys.path.append("/".join([sys.path[0], "mods", modName]))
				#baseMod = importlib.import_module(modName)
				mod = getattr(baseMod, modName)(self)
			except ImportError as error:
				self.logE("[ERROR] Import of mod '%s' failed: %s" % (modName, error))
			else:
				self._loadedMods[modName] = [baseMod, mod]
		self.log("All loaded mods: [%s]"%(", ".join(self.modsList())))

	def reload(self, modName):
		"""
		tries to reload the given mod
		returns status string
		"""
		try:
			baseMod = importlib.reload(self._loadedMods[modName][0])
			mod = getattr(baseMod, key)(self)
		except Exception as e:
			self.logE("Reload of mod '%s' failed: %s" % (modName, e))
		else:
			self._loadedMods[modName] = [baseMod, mod]
			self.log("Reloaded [%s]" % (modName))

	def stop(self, *modsList): 
		"""
		removes mod from active list, will have to be loaded again
		"""
		stopped = []
		for mod in modsList:
			try:
				del self._loadedMods[mod]
			except Exception as e:
				self.logE("Stopping of %s failed: %s" % (mod, e))
			else:
				stopped.append(mod)
		if stopped:
			self.log("Stopped [%s]" % (", ".join(stopped)))

	def _callMods(self, function, *args):
		"""
		finds the mod the command originated form, returns the run command
		search through the mods to find the relevant command 
		"""
		#print(function)
		#print(args)
		for mod in self.modsList():
			#print(self._loadedMods[mod])
			try:
				getattr(self._loadedMods[mod][1], function)(*args)
			except Exception as e:
				self.logE("[MODERROR]: %s" % e)

	def modsList(self):
		"""return loaded mods list"""
		return list(self._loadedMods.keys())








