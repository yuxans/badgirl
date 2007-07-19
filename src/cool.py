#!/usr/bin/env python

# Copyright (c) 2002 Brad Stewart
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

"""cool.py - it's just silly """ 
from moobot_module import MooBotModule
handler_list=["cool"]

class cool(MooBotModule):
	def __init__(self):
		self.regex = "^cool .+"

	def handler(self, **args):
		"""it's just silly"""
		import string
		from irclib import Event

		# Split the string and take every word after the first two as the
		# words to "cool-ify" (first two are the bot name and "cool")
		who = string.join(args["text"].split(" ")[2:])

		# Surround whatever with ":cool:" tags
		text = ":cool: " + who + " :cool:"

		target = self.return_to_sender(args)
		result = Event("privmsg", "", target, [ text ])
       		return result
