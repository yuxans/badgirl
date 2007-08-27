#!/usr/bin/env python

# Copyright (C) 2005 by moo
# Copyright (C) 2007 by FKtPp
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

"""AbilityProfile.py - profile users' ability"""
from moobot_module import MooBotModule
handler_list=["AbilityProfile"]

class StopReply(Exception):
	pass

class AbilityProfile(MooBotModule):
	inqueries = {}
	regex = "^ab(\s+|$)"
	import re
	spaces = re.compile("\s+")
	helps = {
		"grant":   "ab grant <nick> <ability> <score>",
		"despise": "ab despise <ability> <score>",
		"query":   "ab query <nick> [ability]",
		"top":     "ab top",
		"help":    "ab help [ability]",
	}

	def getUserAbilityScore(self, nick, channel, ability):
		import database
		rs = database.doSQL("SELECT score \
				FROM userability ua \
				LEFT JOIN ability ab ON ab.abilityid=ua.abilityid \
				WHERE nick='%s' AND channel='%s' AND ab.name='%s'"
				% (self.sqlEscape(nick), self.sqlEscape(channel), self.sqlEscape(ability))
				)
		try:
			return rs[0][0] or 0
		except:
			return None

	def getUserAbilities(self, nick, channel):
		import database
		return database.doSQL("SELECT ab.name,score \
				FROM userability ua \
				LEFT JOIN ability ab ON ab.abilityid=ua.abilityid \
				WHERE nick='%s' AND channel='%s' \
				ORDER BY score DESC"
				% (self.sqlEscape(nick), self.sqlEscape(channel))
				)

	def setUserAbilityScore(self, nick, channel, abilityid, score, bynick):
		import database
		rs = database.doSQL("REPLACE INTO userability \
				SET nick='%s', channel='%s', abilityid=%d, score=%d, bynick='%s'"
				% (self.sqlEscape(nick), self.sqlEscape(channel), abilityid, score, self.sqlEscape(bynick))
				)
		try:
			return rs[0][0] or 0
		except:
			return None

	def getAbilityId(self, ability, create = False):
		import database
		selGetAbilityId = "SELECT abilityid FROM ability WHERE name='%s'" % self.sqlEscape(ability)

		rs = database.doSQL(selGetAbilityId)
		try:
			abilityid = rs[0][0] or 0
		except:
			abilityid = 0

		if abilityid:
			return abilityid

		if create:
			database.doSQL("INSERT ability(name) VALUES('%s')" % self.sqlEscape(ability))
			return database.doSQL(selGetAbilityId)[0][0]

		return None

	def getTopAbilityUsers(self, channel, ability):
		import database
		abilityid = self.getAbilityId(ability)
		if not abilityid:
			return None

		return database.doSQL("SELECT nick,SUM(score) AS score \
				FROM userability \
				WHERE channel='%s' AND abilityid=%d \
				GROUP BY nick \
				ORDER BY score DESC \
				LIMIT 100"
				% (self.sqlEscape(channel), abilityid)
				)

	def getTopAbilities(self, channel):
		import database

		return database.doSQL("SELECT a.name,SUM(score) AS score \
				FROM userability ua \
				LEFT JOIN ability a ON a.abilityid=ua.abilityid \
				WHERE channel='%s' \
				GROUP BY ua.abilityid \
				ORDER BY score DESC \
				LIMIT 100"
				% (self.sqlEscape(channel))
				)

	def handler(self, **args):
		import string
		from irclib import Event
		import priv

		argv = self.spaces.split(args["text"])
		# case: ~ab
		if len(argv) < 3:
			cmd = None
			argv = []
			argc = 0
		# case ~ab ...
		else:
			cmd = argv[2].lower()
			argv = argv[3:]
			argc = len(argv)

		reply = None

		channel  = self.return_to_sender(args)
		from irclib import nm_to_n
		yournick = nm_to_n(args['source'])
		try:
			from irclib import is_channel
			from ValueModifier import IntValueModifier
			if not is_channel(channel):
				reply = "this is a channel only command"
			elif cmd == "grant":
				if argc != 3:
					raise StopReply()

				import priv
				nick, ability, score = argv
				try:
					print "/%s/" % score
					score = IntValueModifier(score)
				except ValueError:
					reply = "%s: score must be number" % yournick
					raise StopReply()

				curscore = self.getUserAbilityScore(nick, channel, ability) or 0
				score = score.apply(curscore)
				# normal users?
				if priv.checkPriv(args["source"], "ab_admin_priv") == 0 \
					and priv.checkPriv(args["source"], "all_priv") == 0:
					if nick == yournick:
						reply = "You're so proud, %s" % yournick
						raise StopReply()
					yourscore = self.getUserAbilityScore(yournick, channel, ability)
					# apply rules
					if not yourscore or yourscore < score:
						reply = "You don't have enough ability score, %s" % yournick
						raise StopReply()

					if curscore >= score:
						reply = "%s's %s ability is %d already" % (nick, ability, curscore)
						raise StopReply()

				abilityid = self.getAbilityId(ability, True)
				self.setUserAbilityScore(nick, channel, abilityid, score, yournick)
				reply = "%s's %s ability is set to %d" % (nick, ability, score)
			elif cmd == "despise":
				if argc != 2:
					raise StopReply()
				ability, score = argv
				try:
					score = IntValueModifier(score)
				except ValueError:
					reply = "%s: score must be number" % yournick
					raise StopReply()

				curscore = self.getUserAbilityScore(yournick, channel, ability)
				if not curscore:
					reply = "%s: You have no %s ability despise for" % (ability, yournick)
					raise StopReply()

				score = score.apply(curscore)
				if curscore == score:
					reply = "%s: You're yourself" % yournick
				elif curscore <= score:
					reply = "%s: Are you conceited?" % yournick
				else:
					abilityid = self.getAbilityId(ability, True)
					self.setUserAbilityScore(yournick, channel, abilityid, score, yournick)
					reply = "%s has despise himself to %d on %s ability" % (yournick, score, ability)
			elif cmd == "top" or cmd == "help":
				if cmd == "help":
					if argc != 1:
						# module help
						raise StopReply()
					reply = "This function is in TODO"
					raise StopReply()

				from irclib import IrcStringIO
				if argc == 1:
					ability = argv[0]
					user_scores = self.getTopAbilityUsers(channel, ability)
					if not user_scores:
						reply = "no one is capable of %s" % ability
						raise StopReply()
					buffer = IrcStringIO("top user(s) that capable of %s:" % ability)
					for user_score in user_scores:
						buffer.write(" %s*%s" % user_score)
				elif argc == 0:
					ability_scores = self.getTopAbilities(channel)
					if not ability_scores:
						reply = "no one is superman"
						raise StopReply()
					from irclib import IrcStringIO
					buffer = IrcStringIO("top abilities:")
					for ability_score in ability_scores:
						buffer.write(" %s*%s" % ability_score)
				reply = buffer.getvalue()
			else:
				nick    = None
				ability = None
				name    = None # name to guess
				if argc == 0:
					# quick query
					if cmd:
						name = cmd
					else:
						nick = yournick
				elif argc == 1:
					# "query $nick"
					name = argv[0]
				elif argc == 2:
					# "query $nick $ability"
					[nick, ability] = argv
				else:
					raise StopReply()

				# guess if it's nick or ability
				if name:
					abilityid = self.getAbilityId(name)
					if abilityid:
						ability = name
						nick = yournick
					else:
						nick = name
						ability = None
				if nick:
					if ability:
						score = self.getUserAbilityScore(nick, channel, ability) or 0
						if yournick == nick:
							reply = "Your %s ability is %d" % (ability, score)
							if score < 0:
								reply = reply + ". rats!"
						else:
							reply = "%s's %s ability is %d" % (nick, ability, score)
					else:
						ability_scores = self.getUserAbilities(nick, channel)
						if not ability_scores:
							reply = nick + " doesn't have any ability, is he/she disabled?"
						else:
							from irclib import IrcStringIO
							buffer = IrcStringIO(nick + "'s is capable of")
							for ability_score in ability_scores:
								buffer.write(" %s*%s" % ability_score)
							reply = buffer.getvalue()
				else:
					reply = nick + " not found"
		except StopReply:
			pass

		if not reply:
			if cmd == "help" and argc == 0 or not self.helps.has_key(cmd):
				reply = "AbilityProfile: " + " ;; ".join(self.helps.values())
			else:
				reply = "AbilityProfile: " + self.helps[cmd]

		result = Event("privmsg", "", channel, [reply])
		return result
