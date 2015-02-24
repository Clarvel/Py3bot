
from Bot import Bot
import sys

if __name__ == '__main__':
	# system check, verify being run in python3
	if sys.version_info < (3, 0, 0):
		print("This bot must be run in Python3\nUsage: Python3 __init__.py")
		exit(1)
	else:
		bot = Bot()