#!/usr/bin/env python

# Copyright (c) 2002 Vincent Foley
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

from moobot_module import MooBotModule
handler_list = ["getqotd"]

class getqotd(MooBotModule):
	def __init__(self):
		self.regex="^qotd$"

	def handler(self, **args):
		""" Get a quote of the day """
		import os, os.path
	
		if os.path.exists("/usr/games/fortune"):
			fortune = os.popen("/usr/games/fortune")
			message = fortune.read() 
		else:
			message = "Could not get quote: fortune not installed"
	
		target = args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target = nm_to_n(args["source"])
	
	
		from irclib import Event
		result = Event("privmsg", "", target, [ message ])
		return result
