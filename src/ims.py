#!/usr/bin/env python
# -*- encoding: gbk -*-

"""ims.py - used for calc "Biological clock" for a human"""

from moobot_module import MooBotModule
from normalDate import ND
handler_list = ["birthday", "ims"]

class Birthday(MooBotModule):
	def __init__(self, nick):
		self.nick = nick

	def set(self, date):
		"""set yy,mm,dd"""
		import database
		database.doSQL("REPLACE birthday SET nick='%s',birthday='%s'" % (self.sqlEscape(self.nick), self.sqlEscape(date)))

	def get(self):
		"""return timestamp"""
		import database
		b = database.doSQL("SELECT birthday FROM birthday WHERE nick='%s'" % (self.sqlEscape(self.nick)))
		if not b or not b[0]: return False
		b = b[0][0]
		try:
			return ND((b.year, b.month, b.day))
		except:
			return False

	def remove(self):
		import database
		database.doSQL("DELETE FROM birthday WHERE nick='%s'" % (self.sqlEscape(self.nick)))

class agecompare(MooBotModule):
	def __init__(self):
		self.regex="^agecompare\\b"

	def handler(self, **args):
		from irclib import Event, nm_to_n
		params = args['text'].strip().split(' ')[2:]
		if not params or params[0].lower() == 'help':
			msg = 'Usage: agecompare [ |help|$nick[ $nick2]]'
		else:
			nick1 = params[0]
			if len(params) == 2:
				nick2 = params[1]
			else:
				nick2 = nm_to_n(args['source'])
			self.Debug(params)
			b1 = Birthday(nick1).get()
			b2 = Birthday(nick2).get()
			if not b1:
				msg = "Birthday of %s is not set" % (nick1)
			elif not b2:
				msg = "Birthday of %s is not set" % (nick2)
			else:
				self.Debug(b1, b2, nick1, nick2)
				if b1 == b2:
					op = "=="
				elif b1 > b2:
					op = "<"
				else:
					op = ">"
				msg = "age(%s) %s age(%s)" % (nick1, op, nick2)

		return Event("privmsg", "", self.return_to_sender(args), [ msg ])

class birthday(MooBotModule):
	def __init__(self):
		self.regex="^birthday\\b"
		import re
		self.pdate = re.compile("^\\d{4}-\\d{1,2}-\\d{1,2}$")

	def handler(self, **args):
		from irclib import Event, nm_to_n
		params = args['text'].split(' ')[2:]
		if len(params) != 1 or not self.pdate.match(params[0]):
			msg = "Usage: \"birthday YYYY-MM-DD\". You can only set for the nick you're currently using. For privacy, you might want to whisper me."
		else:
			b = Birthday(nm_to_n(args['source']))
			b.set(params[0])
			msg = "Your bithday is set to " + params[0] + ", use \"ims\" to check it"
		return Event("privmsg", "", self.return_to_sender(args), [ msg ])

class ims(MooBotModule):
	msgfmt_setbirtyday = "Use \"birthday YYYY-MM-DD\" to set the birthday for `%s' first. For privacy, whisper is recommended."
	def __init__(self):
		self.regex="^ims(pk)?(?: .*)?"
		import re
		self.pdate = re.compile("^(\\d{4})-(\\d{1,2})-(\\d{1,2})$")

	def handler(self, **args):
		from irclib import Event, nm_to_n
		params = args['text'].strip().split(' ')[1:]
		cmd = params[0]
		params = params[1:]
		dohelp = False
		if len(params) != 0 and len(params) != 1:
			dohelp = True
		elif len(params) == 1 and params[0].lower() == 'help':
			dohelp = True

		if dohelp:
			msg = u"Usage: \"ims [ |help|$nick|YYYY-MM-DD]\", 总数=基数+变数*指数, 指数 in(-1...1) || imspk $nick [$nick2]"
		elif cmd == 'imspk':
			if len(params) == 0:
				msg = "Usage: imspk $nick"
			else:
				if len(params) == 2:
					nick, rival = params
				else:
					nick = nm_to_n(args['source'])
					rival = params[0]
				if nick == rival:
					msg = "%s cannot pk her/himself" % (nick)
				else:
					birthday = Birthday(nick).get()

					if not birthday:
						msg = self.msgfmt_setbirtyday % (nick)
					else:
						rival_birthday = Birthday(rival).get()
						if not rival_birthday:
							msg = self.msgfmt_setbirtyday % (rival)
						else:
							today = ND()
							def sumIms(ims):
								return ims[0] + ims[1] + ims[2]
							n_score = sumIms(self.calcIms(birthday, today))
							r_score = sumIms(self.calcIms(rival_birthday, today))
							if n_score > r_score:
								msg = "%s ROCKS and %s sucks today" % (nick, rival)
							elif n_score < r_score:
								msg = "%s sucks and %s ROCKS today" % (nick, rival)
							else:
								msg = "are %s and %s the same guy?" % (nick, rival)
		# 'ims here'
		elif len(params) == 1 and self.pdate.search(params[0]):
			date = params[0]
			try:
				birthday = ND(date.split('-'))
			except:
				birthday = False
			if birthday:
				msg = self.calc(date, birthday)
			else:
				msg = "date error"
		else:
			if len(params) == 0:
				nick = nm_to_n(args['source'])
			else:
				nick = params[0]
				
			b = Birthday(nick)
			birthday = b.get()

			if birthday:
				msg = self.calc(nick, birthday)
			else:
				msg = self.msgfmt_setbirtyday % (nick)
		return Event("privmsg", "", self.return_to_sender(args), [ msg ])

	def calc(self, calcfor, birthday):
		today = ND()
		tomorrow = today + 1
		(intl1, mood1, str1) = self.calcIms(birthday, today)
		(intl2, mood2, str2) = self.calcIms(birthday, tomorrow)
		return "IMS相对指数 of %s:  智力 %s  情绪 %s  体力 %s (-1...1)".decode("GBK") % (calcfor, self.ud(intl1, intl2), self.ud(mood1, mood2), self.ud(str1, str2))

	def calcIms(self, birthday, day):
		try: import cmath as math
		except: import math

		days = (day - birthday)
		results = []
		for i in [33, 28, 23]:
			mod = days - int(days / i) * i
			deg = 360 * mod / i
			rad = deg * math.pi / 180
			r = math.sin(rad).real
			results.append(r)
		return results

	def ud(self, v1, v2):
		return ("%.2f%s%.2f" % (v1, v1 < v2 and "↑" or "↓", v2)).decode("GBK")
