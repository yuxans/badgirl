#!/usr/bin/env python

# Copyright (c) 2002 Daniel DiPaolo 
# Copyright (C) 2007 by FKtPp
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

from moobot import MooBot, Debug, DebugErr, Handler
import database

class MooBotModule:
	"""Base class for all MooBot modules"""
	from irclib import Event
	class MooBotModuleException(MooBot.MooBotException): pass
	
	regex = "foo"
	type = Handler.LOCAL
	priority = 5 
	stripColor = False
	# the lower this number, the higher the module's priority
	# most modules won't need to change this.

	help_string_short = """
This should be overridden for derived modules.  It should simply contain a
short description of what the module does."""
	help_string_long = """
This should also be overridden for derived modules.  This should contain a
full explanation of what the module does, as well as an example of how to use
it and explanations of syntax conventions.  These should be sort of the man
pages of the modules"""

	def handler(self, **args):
		"""This is the function that actually processes data and returns an
Event.  Should be overridden for every module."""
		self.debug("You forgot to override the 'handler' method.")

	def __cmp__(self, other):
		""" Used for sorting the modules by priority"""
		return cmp(self.priority, other.priority)

	def return_to_sender(self, args, select='auto'):
		"""Returns target for a given event

		assuming we want to return it to the sender, select
		can be one of `auto', `nick', `channel':
		
		auto: returns nick while return to a privmsg, 
		      or returns #channel

		nick, channel: returns its named value
		
		>>> import moobot_module
		>>> x = moobot_module.MooBotModule()
		>>> arg = {'source': 'nick!name@host', 'channel': '#channel', 'type': 'privmsg'}
		>>> x.return_to_sender(arg)
		'nick'
		>>> x.return_to_sender(arg, 'channel')
		'#channel'
		>>> arg = {'source': 'nick!name@host', 'channel': '#channel', 'type': 'notice'}
		>>> x.return_to_sender(arg)
		'#channel'
		>>> x.return_to_sender(arg, 'nick')
		'nick'

		"""
		from irclib import nm_to_n
		if (args["type"] == "privmsg" and \
			    select == 'auto') or \
			    select == 'nick':
			target = nm_to_n(args["source"])
		else: 
			target = args["channel"]
		return target.lower()
	
	def msg_sender(self, args, text, select='auto'):
		target = self.return_to_sender(args)
		return self.Event("privmsg", "", target, [text])

	def privmsg_sender(self, args, text, select='auto'):
		target = self.return_to_sender(args, "nick")
		return self.Event("privmsg", "", target, [text])

	def notice_sender(self, args, text, select='auto'):
		target = self.return_to_sender(args, "nick")
		return self.Event("notice", "", target, [text])

	def getArgs(self, args, skip = 0):
		return args["text"].split()[skip + 1:]

	def getText(self, args, skip = 0):
		return args["text"].split(None, skip + 1)[skip + 1]

	def sqlEscape(self, text):
		""" escapes \ and 's in strings for SQL """

		text = text.replace("\\", "\\\\")
		text = text.replace('"', '\\"')
		text = text.replace("'", "\\'")
		return text

	def addNick(self, nick):
		database.doSQL("INSERT IGNORE seen(nick) VALUES('%s')" % (self.sqlEscape(nick)))
		return self.getNickId(nick)

	def getNickId(self, nick):
		ret = database.doSQL("SELECT nickid FROM seen WHERE nick='%s'" % (self.sqlEscape(nick)))
		if ret and ret[0]:
			return ret[0][0]

	def Debug(self, *args):
		apply(DebugErr, args)

	def debug(self, *args):
		apply(Debug, args)

	def str(self, obj):
		if type(obj) is unicode:
			return obj
		else:
			return str(obj)

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
