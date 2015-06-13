import random
import threading
import os.path
from time import sleep

default_deck_str = "base_deck"


class CAH():
	def __init__(self, callback):
		self.game = CardsAgainstHumanity(callback)

	def COMMAND(self, sender, channel, cmd, message):
		if   cmd == "ch" or cmd == "pl": # choosing an option
			self.game._playerChose(sender, message)
		elif cmd == "jo" or cmd == "join":
			self.game._addPlayer(sender)
		elif cmd == "start":
			self.game._initGame(sender)
		elif cmd == "force":
			self.game._forceStart()
		elif cmd == "scores":
			self.game.printScores()
		elif cmd == "help":
			self.game.help()

class CardsAgainstHumanity():
	def __init__(self, callback):
		#static
		self.reply = callback
		self.maxPlayers = 10 # maximum number of players
		self.minPlayers = 3  # minimum number of players
		self.handLimit = 10  # maximum hand limit, refills to this each turn
		self.maxPoints = 10 # maximum number of points

		self.timeLimit = float(120) # time limit for replies is 2 minutes
		self.playerJoinTimelimit = float(200) # time limit for payers to join

		self.resetDecks()
		self.reset()

	def reset(self): # resets changing values between games
		self.phase = 0 # game phases: 0=not started, 1=initializing, looking for players, 2=playes selecting cards, 3=czar selecting cards
		self.turn = 0 # turn number
		self.whiteDeck = [] # shuffled deck used to play the game
		self.blackDeck = [] # shuffled deck used to play the game
		self.whiteDiscard = []
		self.blackDiscard = []
		self.players = []
		self.replies = [] # tuples of player's replies: (name, reply)
		self.czar = None # which player is the card czar
		self.currBlackCard = None

	def resetDecks(self): # resets the string of decks to load
		self.decks = [default_deck_str] # list of deck names, to be loaded on game start
		#

	def help(self):
		self.reply("Commands: @ch - chooses an option, @pl - plays a card, @jo - joins a starting game, @start - starts a game, @help - prints this, @force - forces game to skip rest of player joining phase")
		#

	def _initGame(self, sender): # initialize the game, spawn thread to wait for players to join
		if self.phase == 0:
			self.reply("Starting a game of Cards Against Humanity. Type '@jo' to join.")
			self.phase = 1

			self._addPlayer(sender)

			timerThread = threading.Thread(target=self.wait, args=[self.startTimedOut, None, self.playerJoinTimelimit])
			timerThread.daemon = True
			timerThread.start()

	def _playerChose(self, sender, cardNumbers): # player chose a card number
		if self.czar.name == sender and self.phase == 3:
			try: # verify czar reply number
				num = int(cardNumbers)-1
				if num < 0 or num >= len(self.players):
					raise Exception("Option Number [%s] not valid" % cardNumbers)
			except Exception as e:
				self.reply("[ERROR]Czar selection failed: %s" % e, sender)
			else:
				pSel = self.replies[num]
				self.reply("Czar chose %s's cards! %s received an Awesome Point!" % (pSel.name, pSel.name))
				pSel.points += 1
				if pSel.points >= self.maxPoints: # if max points reached
					self.reply("%s won the game with %i Awesome Points!" % (pSel.name, pSel.points))
					self.reset() # end the game
				else:
					self.startNewTurn()
		elif self.phase == 2:
			for player in self.players:
				if sender == player.name: # if player found
					numstrs = cardNumbers.split() # get card number strings
					if len(numstrs) != self.currBlackCard.getNumRepliesNeeded(): # ensure correct number of replies is given
						self.reply("[ERROR]Not enough replies: Please choose %i card(s)" % self.currBlackCard.getNumRepliesNeeded(), sender)
						return
					cardsArray = [] # build array of cards to be played
					try:
						for num in numstrs:
							cardInd = int(num)-1
							if cardInd < 0 or cardInd >= len(player.hand):
								raise Exception("Card Number [%s] not valid" % num)
							reps = findRepetitions(num, numstrs) # prevent trying to pick the same card multiple times
							if reps > 1:
								raise Exception("Can't select [%i] %i times!" % (num, reps))
							cardsArray.append(cardInd)
					except Exception as e:
						self.reply("[ERROR]Card selection failed: %s" % e, sender)
						return
					else:
						player.playing = cardsArray # move card indexes to waiting pile
						
						cardStrs = []
						for cardInd in cardsArray:
							cardStrs.append(player.hand[cardInd])
						self.reply("You played: [%s]." % ", ".join(cardStrs), player.name)

						for player in self.players: # check if all replies are submitted
							if len(player.playing) != self.currBlackCard.getNumRepliesNeeded():
								return
						self.startCzarPhase("pchose")

	def _addPlayer(self, sender): # add player to list of players
		if self.phase == 1:
			for player in self.players: # ensure sender has not already joined
				if sender == player.name:
					self.reply("You can't join the same game twice.", sender)
					return
			self.players.append(Player(sender)) # add player to game
			self.reply("%s joined Cards Against Humanity" % sender)

			if len(self.players) >= self.maxPlayers: # if max players reached, begin the game immediately
				self.beginGame()

	def _forceStart(self): # forces start of game if able
		if self.phase == 1 and len(self.players) >= self.minPlayers:
			self.beginGame()

	def loadShuffleDecks(self): # loads and shuffles the decks specified
		for deck in self.decks:
			whitePath = os.path.join(os.path.dirname(__file__), "%s/white_cards.txt" % deck)
			blackPath = os.path.join(os.path.dirname(__file__), "%s/black_cards.txt" % deck)

			white = open(whitePath)
			black = open(blackPath)

			self.whiteDeck += white.read().splitlines()
			self.blackDeck += black.read().splitlines()

		random.shuffle(self.whiteDeck)
		random.shuffle(self.blackDeck)

	def wait(self, callback, callBackVars = None, customTime = None): # waits the specified ammount of time, then calls the callback function
		if customTime is None:
			sleep(self.timeLimit)
		else: 
			sleep(float(customTime))

		if callBackVars is not None:
			callback(callBackVars)
		else:
			callback()

	def startTimedOut(self): # called once the specified time has elapsed for new players to join, passes silently if max players joined
		if self.phase == 1 and len(self.players) != self.maxPlayers: # if equal to max players, game has already started, pass silent
			if len(self.players) >= self.minPlayers: # enough players, begin the game
				self.beginGame()
			else: # not enough players
				self.phase = 0
				self.reply("Could not start game, too few players")
				self.reset()

	def playerTimedOut(self, currTurn): # called once the end for players picking has elapsed, pases silently if all players have picked appropros cards [[TODO]]
		if self.phase == 2 and self.turn == currTurn:
			numReplies = 0
			for player in self.players:
				if len(player.playing) == 0:
					player.points -= 1
					self.reply("%s has lost an awesome point for failing to play!" % player.name)
				else:
					numReplies += 1
			if numReplies < self.minPlayers-1:
				self.reply("Not enough replies to continue turn, skipping...")
				self.startNewTurn()
			else:
				self.startCzarPhase("ptimeout")

	def startCzarPhase(self, a): # begins czar phase
		print(a)
		self.phase = 3
		self.replies = [] # tuples of replies
		self.reply("Czar %s, choose best from this list:" % self.czar.name)
		for player in self.players:
			if(len(player.playing) != 0):
				self.replies.append(player)
		for a in range(0, len(self.replies)):
			cList = self.replies[a].getPlayedCardsList() # get playd cards
			self.reply("(%i) %s" % (a+1, self.currBlackCard.getFilledStr(cList)))
			self.whiteDiscard += cList # send cards to discard once played
		self.wait(self.czarTimedOut, self.turn)

	def czarTimedOut(self, currTurn): # called once the end for czar picking has elapsed, pases silently if has picked
		if self.phase == 3 and self.turn == currTurn:
			self.czar.points -= 1
			self.reply("%s has lost an awesome point for failing to play!" % self.czar.name)
			self.startNewTurn()

	def dealCards(self): # deal cards up to the hand limit, show to player
		for player in self.players:
			numToFill = self.handLimit - len(player.hand)
			for a in range(0, numToFill):
				player.hand.append(self.getWhiteCard())
			reply = "%s, Your hand: [(%i) %s" % (player.name, 1, player.hand[0])
			for a in range(1, len(player.hand)):
				reply += ", (%i) %s" % (a+1, player.hand[a])
			reply += "]"
			self.reply(reply, player.name)

	def chooseCzar(self): # chooses new czar
		if self.czar is not None: # add last czar back to list of players
			self.players.append(self.czar)
		self.czar = self.players.pop(0)
		self.reply("%s is the new Czar!" % self.czar.name)

	def startNewTurn(self): # begins new turn
		self.phase = 2
		self.turn += 1
		for player in self.players: # unmark all people who've played
			player.playing = []
		self.chooseCzar() # change the czar
		self.dealCards() # deal out any missing cards
		self.newBlackCard() # make new active black card
		self.wait(self.playerTimedOut, self.turn)

	def newBlackCard(self): # pops a black card from the black deck
		if self.currBlackCard != None:
			self.blackDiscard.append(self.currBlackCard.getCardStr())
		self.currBlackCard = BlackCard(self.getBlackCard())
		self.reply("New Black Card: %s" % self.currBlackCard.getBlankStr())

	def getWhiteCard(self):
		if not self.whiteDeck: # if white deck is empty
			self.whiteDeck = self.whiteDiscard
			random.shuffle(self.whiteDeck)
		return self.whiteDeck.pop()

	def getBlackCard(self):
		if not self.blackDeck:
			self.blackDeck = self.blackDiscard
			random.shuffle(self.blackDeck)
		return self.blackDeck.pop()

	def beginGame(self): # begins the game proper
		self.reply("Starting Cards Against humanity!")
		self.reply("Play cards using @pl (list of numbers), example for 2 cards: @pl 1 4")
		random.shuffle(self.players) # shuffle list of players
		self.loadShuffleDecks()
		self.startNewTurn()	

class Player(): # tracks player variables
	def __init__(self, name):
		self.name = name
		self.hand = [] # list of white cards
		self.playing = [] # list of hand index refrences
		self.points = 0

	def getPlayedCardsList(self):
		play = []
		hand = []
		for a in range(0, len(self.hand)):
			if a in self.playing:
				play.append(self.hand[a])
			else:
				hand.append(self.hand[a])
		self.hand = hand
		return play

class BlackCard(): # current black card class, used to fill in with white cards
	def __init__(self, cardStr):
		self.cardStr = cardStr
		self.strList = cardStr.split("%s")
		self.numRepliesNeeded = len(self.strList)-1
		if self.numRepliesNeeded == 0:
			self.numRepliesNeeded = 1

	def getBlankStr(self):
		return "___".join(self.strList)

	def getFilledStr(self, fillList):
		if len(fillList) != self.numRepliesNeeded:
			raise Exception("Not enough filled options")

		complete = self.strList[0] # build completed string
		for a in range(1, len(self.strList)):
			complete += " [%s] %s" % (fillList[a-1], self.strList[a])
		return complete

	def getNumRepliesNeeded(self):
		return self.numRepliesNeeded
		#
	def getCardStr(self):
		return self.cardStr

def findRepetitions(val, list): # return number of repetitions in a list
	reps = 0
	for a in list:
		if a == val:
			reps += 1
	return reps

