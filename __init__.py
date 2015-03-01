
from IRCClient import IRCClient
import sys

if __name__ == '__main__':
	# system check, verify being run in python3
	if sys.version_info < (3, 3, 2):
		print("This bot must be run in Python3\nUsage: python3 __init__.py")
		exit(1)
	else:
		bot = IRCClient()
		bot.listen()