#!/usr/bin/env python
# -*- encoding: gbk -*-

"""ims.py - used for calc "Biological clock" for a human"""

from moobot_module import MooBotModule
handler_list = ["birthday", "ims"]

privCache = None

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
		b = database.doSQL("SELECT UNIX_TIMESTAMP(birthday) FROM birthday WHERE nick='%s'" % (self.sqlEscape(self.nick)))
		if not b or not b[0]: return False
		return int(b[0][0])

	def remove(self):
		import database
		database.doSQL("DELETE FROM birthday WHERE nick='%s'" % (self.sqlEscape(self.nick)))

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
	def __init__(self):
		self.regex="^ims(?: .*)?"
		import re
		self.pdate = re.compile("^(\\d{4})-(\\d{1,2})-(\\d{1,2})$")

	def handler(self, **args):
		from irclib import Event, nm_to_n
		params = args['text'].split(' ')[2:]
		dohelp = False
		if len(params) != 0 and len(params) != 1:
			dohelp = True
		elif len(params) == 1 and params[0].lower() == 'help':
			dohelp = True

		if dohelp:
			msg = "Usage: \"ims [ |help|$nick|YYYY-MM-DD]\""
		elif len(params) == 1 and self.pdate.search(params[0]):
			import time
			date = params[0]
			birthday = time.mktime(time.strptime(date, "%Y-%m-%d"))
			msg = self.calc(date, birthday)
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
				msg = "Use \"birthday YYYY-MM-DD\" to set birthday for `%s' first. For privacy, whisper is recommended." % (nick)
		return Event("privmsg", "", self.return_to_sender(args), [ msg ])

	def calc(self, calcfor, birthday):
		import time
		today = time.time()
		tomorrow = today + 24 * 60 * 60
		(intl1, mood1, str1) = self.calcIms(birthday, today)
		(intl2, mood2, str2) = self.calcIms(birthday, tomorrow)
		return "IMS of %s:  智力 %s  情绪 %s  体力 %s (-1...1)".decode("GBK") % (calcfor, self.ud(intl1, intl2), self.ud(mood1, mood2), self.ud(str1, str2))

	def calcIms(self, birthday, day):
		try: import cmath as math
		except: import math

		days = int((day - birthday) / (24 * 60 * 60))
		results = []
		for i in [33, 28, 23]:
			mod = days % i
			deg = 360 * mod / i
			rad = deg * math.pi / 180
			r = math.sin(rad).real
			results.append(r)
		return results

	def ud(self, v1, v2):
		return ("%.2f%s%.2f" % (v1 + 0.05, v1 < v2 and "↑" or "↓", v2 + 0.05)).decode("GBK")
