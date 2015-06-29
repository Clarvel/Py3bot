"""
adds moddable capacity to the IRC server
allows for loading, reloading and stopping of mods while running
mods are executed using the _callMods function, 
	with the specified mod function and the specified args

Matthew Russell
june 29, 2015
"""
#system imports
import sys
import importlib
import traceback

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
		loaded = []
		for modName in modsList:
			path = "%s/mods/%s" % (sys.path[0], modName)
			if path not in sys.path:
				sys.path.append(path)
			try:
				baseMod = importlib.import_module(modName)
				mod = getattr(baseMod, modName)(self)
			except ImportError as error:
				self.logE("[ERROR] Import of mod '%s' failed: %s" % (modName, 
					error))
				sys.path.pop()
			except Exception as e:
				self.logE("An error occured on loading %s: %s" % (modName, e))
				print(traceback.format_exc())
			else:
				self._loadedMods[modName] = [baseMod, mod, path]
				loaded.append(modName)
		self.log("Loaded %s" % loaded)

	def reload(self, modName):
		"""
		tries to reload the given mod
		returns status string
		"""
		try:
			baseMod = importlib.reload(self._loadedMods[modName][0])
			mod = getattr(baseMod, modName)(self)
		except KeyError as e:
			self.logE("No module named %s found" % e)
		except AttributeError as e:
			self.logE("Mod '%s' has not yet been loaded: %s" % (modName, e))
		except Exception as e:
			self.logE("Reload of mod '%s' failed: %s" % (modName, e))
			print(traceback.format_exc())
		else:
			self._loadedMods[modName] = [baseMod, mod, 
				self._loadedMods[modName][2]]
			self.log("Reloaded [%s]" % (modName))

	def stop(self, *modsList): 
		"""
		removes mod from active list, will have to be loaded again
		"""
		stopped = []
		for mod in modsList:
			try:
				sys.path.remove(self._loadedMods[mod][2])
				del sys.modules[mod]
				del self._loadedMods[mod]
			except KeyError as e:
				self.logE("No module named %s found" % e)
			except Exception as e:
				self.logE("Stopping of '%s' failed: %s" % (mod, e))
				print(traceback.format_exc())
			else:
				stopped.append(mod)
		if stopped:
			self.log("Stopped %s" % stopped)

	def _callMods(self, function, *args):
		"""
		finds the mod the command originated form, returns the run command
		search through the mods to find the relevant command 
		"""
		for mod in self.modsList():
			try:
				getattr(self._loadedMods[mod][1], function)(*args)
			except Exception as e:
				self.logE("[MODERROR]: %s" % e)
				print(traceback.format_exc())


	def modsList(self):
		"""return loaded mods list"""
		return list(self._loadedMods.keys())








