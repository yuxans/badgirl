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

"""eventProcess.py - process Events """

handler_list=["eventProcess"]

from moobot_module import MooBotModule
from utilities import *

class eventProcess(MooBotModule):
	def __init__(self):
		self.type="all"

	def handler(self, **args):
		"""Does an appropriate action based on event"""

		bot = args["ref"]() # resolve the reference to the bot
		event = args["event"]
        if event.eventtype() == "privmsg" and event.target().lower() != bot.connection.get_nickname().lower():
     		for line in event.arguments()[0].split("\n"):
 				if line != "":
 					bot.connection.privmsg(event.target(), line)
        elif event.eventtype() == "action":
            bot.connection.action(event.target(), event.arguments()[0])
        elif event.eventtype() == "continue":
            return
