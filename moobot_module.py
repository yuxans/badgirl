#!/usr/bin/env python

# Copyright (c) 2002 Daniel DiPaolo 
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

from moobot import MooBot
from moobot import Handler

class MooBotModule:
	"""Base class for all MooBot modules"""
	from irclib import Event
	class MooBotModuleException(MooBot.MooBotException): pass
	
	regex = "foo"
	type = Handler.LOCAL
	priority = 5 
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

	def __init__(self):
		pass
	
	def handler(self, **args):
		"""This is the function that actually processes data and returns an
Event.  Should be overridden for every module."""
		print "You forgot to override the 'handler' method."

	def __cmp__(self, other):
		""" Used for sorting the modules by priority"""
		return cmp(self.priority, other.priority)

	def return_to_sender(self, args):
		"""Returns target for a given event, assuming we want to return it to the sender"""
		from irclib import nm_to_n
		if args["type"] == "privmsg": target = nm_to_n(args["source"])
		else: target = args["channel"]
		return target
	
	def sqlEscape(self, text):
		""" escapes \ and 's in strings for SQL """
		import string
		text = string.replace(text, "\\", "\\\\")
		text = string.replace(text, "'", "\\'")
		return text
			
