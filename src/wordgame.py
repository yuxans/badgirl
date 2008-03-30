#!/usr/bin/env python

# Copyright (c) 2002 Keith Jones
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

""" wordgame.py  - a simple hangman-like game
    
access wordgame with the wg command any one of the following:
	
new      - start a new game
guess x  - make a guess	on current game (x is single character)
show     - show current clue and list of guessed letters
answer x - propose answer (x is the word you think it is)
score  x - show scores x is 'high', 'low', or a list of nicks
	
"""

from moobot_module import MooBotModule
handler_list = ["wordgame"]

BLANK = '_'
WGTYPE = 'wgscore'

class wordgame(MooBotModule):
	def __init__(self):
		""" intialize the wordgame module"""
		
		self.regex="^wg\s+.*"
		self.state = 'off'
		self.words = ['Banana', 'Walrus', 'Plasma', 'TheLinuxDuck']
		self.index = 0
		self.clue = ''
		self.letters = ''
		self.channels = []
		
		
	def handler(self, **args):
		""" handle a wordgame message """
		from irclib import Event, nm_to_n

		message = "crap on a stick"
		input = args["text"].split()
		
		who = nm_to_n(args["source"])

		# parsing input
		try:
			cmd = input[2]
		except IndexError:
			cmd = 'none'

		try:
			rest = " ".join(input[3:])
		except IndexError:
			rest = 'none'

		#handle various commands
		cmd = cmd.lower()
		
		if cmd == 'chan':
			if rest.strip() == '':
				if len(self.channels) == 0:
					message = "any channel"
				else:
					message =  "okay channels: " + str(self.channels)
			else: 
				message = self.do_chan(args["source"], input[3:]) 
			return Event("privmsg", "", self.return_to_sender(args), [message])

			
		if args["channel"] not in self.channels and len(self.channels) != 0:
			message = 'wg now only works in the following channels,' +\
			          'so as not to piss everyone off: ' + str(self.channels)
			return Event("privmsg", "", self.return_to_sender(args), [message])


		if cmd == 'none':
			message =\
			'wordgame: wg new|(g)uess x|(s)how|(a)nswer xxxx|score [NICKS|high|low|chan'

		elif cmd in ['g', 's', 'a', 'guess', 'show', 'answer'] and self.state == 'off':
			message = 'no game in progress, ' + who + ', use "wg new"'

		elif cmd == 'new':
			if self.state != 'off':
				message = 'game already in progress: ' + self.clue
			else:
				self.new_game()
				message = self.clue

		elif cmd in ['guess', 'g']:
			rest.strip()
			if len(rest) != 1:
				self.debug(len(rest), "'" + rest + "'")
				message = "only one character please, " + who
			else:
				message = self.do_guess(rest, who)

		elif cmd in ['show', 's']:
			self.letters = map(lambda x: x, self.letters)
			self.letters.sort()
			self.letters = " ".join(self.letters).strip()
			message = self.clue + ' guessed: ' + self.letters

		elif cmd in ['answer', 'a']:
			rest.strip()
			if rest.lower() != self.answer.lower():
				self.score(who, 'LOSE')
				message = "Wrong Answer," + who + ". score: "\
							+ str(self.get_score(who))
			else:
				self.score(who, 'WIN', self.clue.count(BLANK))					
				message = "Right, " +  who + "! " + "score: "\
				          + str(self.get_score(who))
				self.reset()

		elif cmd == 'score':
			scores = self.get_score_map()
			if rest == 'none': rest = 'high'
			if rest in ['high', 'low']:
				items = scores.items()
				items.sort(self.cmp_pair_by_second)
				if len(items) < 5:
					cnt = len(items)
				else:
					cnt = 5
				if   rest == 'low': message = 'low scores: ' + str(items[:cnt])
				elif rest == 'high' : message = 'high scores:' + str(items[-cnt:])
				else: pass

			else:
				message = 'score(s): '
				for nick in input[3:]:
					try:
						score = scores[nick]
					except KeyError:
						score = 0
					message += "%s: %d; " % (nick, score)
					
		return Event("privmsg", "", self.return_to_sender(args), [ message ])
		

	def get_new_answer(self):
		""" Retrieves a random word for codeexamples.org """
		import httplib

		conn = httplib.HTTPConnection('www.codeexamples.org')
		conn.request("GET", '/cgi-bin/randomword.cgi')
		resp = conn.getresponse()

		if resp.status != 200:
			self.debug('Ack! Falling back on hardcoded words...')
			self.index += 1
			if self.index >= len(self.words):
				self.index = 0
			return self.words[self.index]
		else: 
			self.debug('using codeexamples.org word')
			word = resp.read()
			conn.close()
			word = word.strip()

			return word
			
		
	def do_guess(self, guess, who):
		""" process a guess """

		answer_letters = map(lambda x: x, self.answer)
		clue_letters = map(lambda x: x, self.clue)

		if guess in self.letters:
			return guess + " has already been guessed"
		else:
			self.letters += guess

		for x in range(len(self.answer)):
			if clue_letters[x] == BLANK and\
			answer_letters[x].lower() == guess.lower():
			   clue_letters[x] = answer_letters[x]

		if " ".join(clue_letters) != self.clue:
			self.clue = " ".join(clue_letters)
			self.score(who, 'GUESS', self.clue.count(guess))
			if BLANK not in self.clue:
				self.reset()
				return "Right, " +who+ "! score: " + str(self.get_score(who))
			else:
				return "good guess, "+ who +" ("+str(self.get_score(who))+"): "\
			       + self.clue
		else:
			self.score(who, 'GUESS')
			return "bad guess, " + who + " (" + str(self.get_score(who)) + ")"


	def score(self, who, type, opt=0):
		""" modify score for a user """
	
		import database
		
		current = self.get_score(who)
			
		if type == 'WIN':
			current = current + (opt*10) + 15
		elif type == 'LOSE':
			current -= 15
		elif type == 'GUESS':
			current = (current - 5) + (opt*10)
		
		database.doSQL("update stats set counter = "+ str(current)+" where nick = '" + who + "' and type= '" + WGTYPE+"'")


	def reset(self):
		""" clean up all old game info """
		self.state = 'off'
		self.answer = ''  # unnecessary
		self.clue =  '' 
		self.letters = ''


	def cmp_pair_by_second(self, par1, par2):
		""" compare two 2-tuples by the second item in them """
		(x1, y1) = par1
		(x2, y2) = par2
		if y1 < y2: return -1
		if y2 < y1: return 1
		return 0
		

	def new_game(self):
		""" start a new game """
		self.state = 'on'
		self.answer = self.get_new_answer()
		self.clue = BLANK * len(self.answer)


	def get_score(self, who):
		""" retrieve a single nick,score pair from the database """
		
		import database
		
		results=database.doSQL("select counter from stats where nick = '" + who + "' and type = '" + WGTYPE + "'")
		if len(results) == 0:
			database.doSQL("insert into stats values( '" + who + "', '" + WGTYPE + "', 0)")
			score = 0
		else:
			score = int(results[0][0])
		
		return score


	def get_score_map(self):
		""" retrieve all (nick, score) pairs from the database """

		import database

		results=database.doSQL("select nick, counter from stats where type = '" + WGTYPE + "'")
		if len(results) == 0:
			return {}
		else:
			scores = {}
			for (nick, score) in results:
				try:
					score = int(score)
				except ValueError:
					score = 0
				scores[nick] = score
				
			return scores

	def do_chan(self, mask, input):
		import priv
		if priv.checkPriv(mask, "all_priv") == 0:
			return "I don't have to listen to you."
		else:
			try:
				if input[0] == '+':
					for chan in input[1:]:
						self.channels.append(chan)
				elif input[0] == '-':
					for chan in input[1:]:
						try:
							self.channels.remove(chan)
						except ValueError: pass
				message = 'ok'
			except IndexError:
				message = "you didn't seem to provide valid input."
			return message
