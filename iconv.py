#!/usr/bin/env python

from irclib import Event
from moobot_module import MooBotModule
from handler import Handler
handler_list = ["iconv", "iconvMsg"]

class iconv(MooBotModule):
	def __init__(self):
		self.regex = "^(?:iconv (from|to) \S+ .+)$"

	def handler(self, **args):
		(cmd, encoding) = args['text'].split(' ', 4)[2:4]
		if cmd.lower() == 'from':
			rawmsg = args['event'].rawdata().split(' ', 6)[6]
			msg = rawmsg.decode(encoding, 'replace')
		else:
			msg = "not implemented"

		return Event("privmsg", "", self.return_to_sender(args), [ msg ])

class iconvMsg(MooBotModule):
	def __init__(self):
		self.regex = ""
		import re
		utf8char = "(?:[\xE0-\xEF][\x80-\xFE]{2})"
		self.preg = re.compile("^%s{2,20}" % (utf8char))
		self.type = Handler.GLOBAL
		self.priority = 100

	def handler(self, **args):
		rawmsg = args['event'].rawdata().split(' ', 3)[3][1:]
		if not self.preg.search(rawmsg):
			return Event("continue", "", "")

		try:
			msg = rawmsg.decode('utf-8')
		except Exception, e:
			self.Debug(e)
			return Event("continue", "", "")

		from irclib import nm_to_n
		msg = nm_to_n(args['source']) + ' says: ' + msg
		return Event("privmsg", "", self.return_to_sender(args), [ msg ])
