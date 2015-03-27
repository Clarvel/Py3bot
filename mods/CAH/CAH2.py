import random
import threading
import os.path
from time import sleep

default_deck_str = "base_deck"

class Default():
	def __init__(self, callback):
		self.game = CAH(callback)

	def COMMAND(self, sender, channel, cmd, message):
		if self.game.playing(): # if playing the game
			if cmd == "ch": # choosing an option
				self.game.playerChose(sender, message)
			if cmd == "forfeit":
				self.game.dropPlayer(sender)
			if cmd == "stopVote":
				self.game.stopVote(sender)
			elif cmd == "jo":
				self.game.addPlayer(sender)
			elif cmd == "players":
				self.game.listPlayers()
		if cmd == "cah": # THIS is indicated as target
			words = message.split() # make list of words
			subcmd = words.pop(0) # first word is actual command
			if not self.game.playing(): # not playign game options
				if subcmd == "start":
					self.game.initGame(channel, sender)
				elif subcmd == "addDeck":
					self.game.addDeck(*words)
				elif subcmd == "delDeck":
					self.game.deldeck(*words)
				elif subcmd == "resetDecks":
					self.game.resetDecks()
				elif subcmd == "currDecks":
					self.game.showCurrDecks()
				elif subcmd == "setTimeLimit":
					self.game.setTimeLimit(*words)
				elif subcmd == "setPassLimit":
					self.game.setPassLimit(*words)
			if sucmd == "help":
				self.game.printHelpTo(channel)

class CAH():
	def __init__(self, callback):
		#static
		self.reply = callback
		self.maxPlayers = 10 # maximum number of players
		self.minPlayers = 3  # minimum number of players
		self.handLimit = 10  # maximum hand limit, refills to this each turn

		self.timeLimit = 120 # time limit for replies is 2 minutes
		self.playerJoinTimelimit = 300 # time limit for payers to join
		self.mainChan = None # main channel people are playing in

		self.resetDecks()
		self.reset()

	def reset(self): # resets changing values between games
		self.phase = 0 # game phases: 0=not started, 1=initializing, looking for players, 2=playes selecting cards, 3=czar selecting cards
		self.whiteDeck = [] # shuffled deck used to play the game
		self.blackDeck = [] # shuffled deck used to play the game
		self.whiteDiscard = []
		self.blackDiscard = []
		self.players = []
		self.czar = None # which player is the card czar
		self.currBlackCard = None

	def resetDecks(self): # resets the string of decks to load
		#
		self.decks = [default_deck_str] # list of deck names, to be loaded on game start

	def initGame(self, channel, sender): # initialize the game, spawn thread to wait for players to join
		self.mainChan = channel # for replying to main channel
		self.reply("Starting a game of Cards Against Humanity. Type 'jo' to join.", self.mainChan)
		self.phase = 1

		timerThread = threading.Thread(target=self.wait, args=[self.startTimeOut, self.playerJoinTimelimit])
		timerThread.daemon = True
		timerThread.start()

	def playerChose(self, sender, cardNumber): # player chose a card number [[TODO]]
		for player in self.players:
			if sender == player.name:
				try:
					cardInd = int(cardNumber)
					if cardInd <= 0 or cardInd >= len(player.hand):
						raise Exception("Card Number [%s] not valid" % cardInd)
				except Exception as e:
					self.reply("[ERROR]Card selection failed: %s" % e, sender)
				else:
					player.playing.append(player.hand.pop(cardInd)) # ???
					player.played = True
					# move card to waiting pile, mark with

	def addPlayer(self, sender): # add player to list of players
		for player in self.players: # ensure sender has not already joined
			if sender == player.name:
				self.reply("You can't join the same game twice.", sender)
				return
		self.players.append(Player(sender)) # add player to game
		self.reply("%s joined Cards aAgainst Humanity" % sender)

		if len(self.players) == self.maxPlayers: # if max players reached, begin the game immediately
			self.beginGame()

	def dropPlayer(self, sender): # player forefeits and loses the game [[TODO]]
		# TODO what should be done about white cards already in play?
		for player in self.players:
			if player.name == sender: # if player is in the game
				self.reply("%s forfeited" % sender, self.mainChan)

				if len(self.players)-2 < self.minPlayers: # check if enough players to continue the game
					self.reply("Not enough players to continue the game", self.mainChan)
					self.endGame()
					return

				self.whiteDiscard += player.hand # add their hand to the discard

				self.players.remove(player)

		if czar.name == sender: # if player is in the game
			self.reply("%s forfeited" % sender, self.mainChan)

			if len(self.players)-1 < self.minPlayers: # check if enough players to continue the game
				self.reply("Not enough players to continue the game", self.mainChan)
				self.endGame()
				return
			self.whiteDiscard += czar.hand # add their hand to the discard

			self.chooseCzar() # choose new czar

	def stopVote(self, sender): # if all players agree to stop, game ends no winner
		for player in self.players+[self.czar]:
			if sender == player.name:
				self.reply("%s voted to end the game." % player, self.mainChan)
				player.continueVote = False

				for playr in self.players: # check if game should end
					if playr.continueVote: # if at least 1 person wants to continue
						return
				self.reply("Game ended by vote.", self.mainChan)
				self.endGame()

	def listPlayers(self): # send list of players to main channel
		if self.mainChan != None:
			pList = []
			for player in self.players+[self.czar]:
				pList.append(player.name)
			self.reply("Players: %s" % (pList), self.mainChan)

	def addDeck(self, deckName): # adds specified deck to the deckList
		if os.path.exists("%s/white_cards.txt" % deckName) and os.path.exists("%s/black_cards.txt" % deckName):
			self.decks.append(deckName)
		else:
			self.reply("[ERROR]Could not find deck [%s]" % deckName, self.mainChan)

	def delDeck(self, deckName): # removes specified deck from the deckList
		if len(self.decks) <= 1:
			self.reply("[ERROR]Cannot remove to fewer than 1 decks!", self.mainChan)
			return

		try:
			self.decks.remove(deckName)
		except Exception as e:
			self.reply("[ERROR]Could not remove deck [%s]: %s" % (deckName, e))
		else:
			self.reply("Removed deck %s from the list" % deckName)

	def showCurrDecks(self): # show all currently used decks
		if self.mainChan != None:
			decks = []
			for key in self.decks.keys():
				decks.append(self.decks[key][0])
			self.reply("Decks: " + decks, self.mainChan)

	def setTimeLimit(self, number): # sets timeout limit for turn choosing
		try:
			self.timeLimit = int(number)
		except Exception as e:
			self.reply("[ERROR]Set time limit failed: %s" % e)

	def loadShuffleDecks(self): # loads and shuffles the decks specified
		for deck in self.decks:
			white = open("%s/white_cards.txt" % deck)
			black = open("%s/black_cards.txt" % deck)

			self.whiteDeck += white.readlines()
			self.blackDeck += black.readlines()

		random.shuffle(self.whiteDeck)
		random.shuffle(self.blackDeck)

	def wait(self, callback, customTime = None): # waits the specified ammount of time, then calls the callback function
		if customTime != None:
			sleep(self.timeLimit)
		else: 
			sleep(customTime)
		callback()

	def startTimeOut(self): # called once the specified time has elapsed for new players to join, passes silently if max players joined
		if len(self.players) != self.maxPlayers: # if equal to max players, game has already started, pass silent
			if len(self.players) >= self.minPlayers: # enough players, begin the game
				self.beginGame()
			else: # not enough players
				self.phase = 0
				self.reply("Could not start game, too few players", self.mainChan)

	def playerTimeOut(self): # called once the end for players picking has elapsed, pases silently if all players have picked appropros cards [[TODO]]
		for player in self.players:
			if not player.playedTurn:
				player.points -= 1
				self.reply("%s has lost awesome ponts for failing to play!" % player.name, self.mainChan)
		self.playerPhaseEnd()
	def playerPhaseEnd(self):
		#TODO if 0 replies, skip turn
		#TODO czar chooses from list

	def czarTimeOut(self): # called once the end for czar picking has elapsed, pases silently if has picked
		if not self.czar.playedTurn:
			self.czar.points -= 1
			self.reply("%s has lost awesome ponts for failing to play!" % self.czar.name, self.mainChan)
			self.czarPhaseEnd()
			
	def czarPhaseEnd(self):
		

	def dealCards(self): # deal cards up to the hand limit, show to player
		for player in self.players:
			numToFill = self.handLimit - len(player.hand)
			for a in range(0, numToFill):
				player.hand.append(self.drawWhiteCard())
			self.reply("Hand: " + player.hand, player.name)

	def chooseCzar(self): # chooses new czar
		if(self.czar != None):
			self.players.append(self.czar)
		self.czar = self.players.pop(0)

	def startNewTurn(self): # begins new turn
		self.phase = 2
		for player in self.players: # unmark all people who've played
			player.playedTurn = False
		self.dealCards() # deal out any missing cards
		self.chooseCzar() # change the czar
		self.newBlackCard() # make new active black card
		self.wait(self.playerTimeOut)

	def newBlackCard(self): # pops a black card from the black deck
		self.currBlackCard = BlackCard(self.blackDeck.pop())
		self.reply("New Black Card: %s" % self.currBlackCard.getBlankStr(), self.mainChan)
	def drawWiteCard(self): # pops white card off deck and returns it to calling function
		#
		return self.whiteDeck.pop()

	def beginGame(self): # begins the game proper
		self.reply("Starting Cards Against humanity!", self.mainChan)
		random.shuffle(self.players) # shuffle lis of players
		self.loadShuffleDecks()
		self.startNewTurn()	
	def endGame(self):

class Player(): # tracks player variables
	def __init__(self, name):
		self.name = name
		self.hand = [] # list of white cards
		self.playing = [None]
		self.playedTurn = False
		self.points = 0
		self.continueVote = True

class BlackCard(): # current black card class, used to fill in with white cards
	def __init__(self, cardStr):
		self.strList = cardStr.split("%s")

	def getBlankStr(self):
		return self.strList.join("___")

	def getFilledStr(self, fillList):
		if len(fillList)+1 != len(self.strList):
			raise Exception("Not enough filled options")

		complete = self.strList[0] # build completed string
		for a in range(1, len(self.strList)):
			complete += " [%s] %s" % (fillList[a-1], self.strList[a])
		return complete



