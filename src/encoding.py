#!/usr/bin/env python

from irclib import Event
from moobot_module import MooBotModule
from handler import Handler
handler_list = ["decodeUtf8"]

# auto decode utf-8
class decodeUtf8(MooBotModule):
	def __init__(self):
		self.regex = ""
		import re
		utf8char = "(?:[\xE0-\xEF][\x80-\xBF]{2})"
		self.preg = re.compile("%s%s" % (utf8char, utf8char))
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
