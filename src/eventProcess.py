#!/usr/bin/env python

# Copyright (c) 2002 Brad Stewart
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
		if event.source() == bot.connection.get_nickname():
			# self.Debug("%s %s %s %s" % (event.source(), event.eventtype(), event.target(), bot.connection.get_nickname()))
			if event.eventtype() == "privmsg":
				for line in event.arguments()[0].split("\n"):
					if line != "":
						bot.connection.privmsg(event.target(), line)
				return # done
			
			elif event.eventtype() == "notice":
				for line in event.arguments()[0].split("\n"):
					if line != "":
						bot.connection.notice(event.target(), line)
				return # done

			elif event.eventtype() == "action":
				bot.connection.action(event.target(), event.arguments()[0])
				return # done

			elif event.eventtype() == "ctcp":
				texts = event.arguments()[0].split(" ", 1)
				if len(texts) == 1:
					(ctcptype, ctcptext) = (texts[0], "")
				else:
					(ctcptype, ctcptext) = texts
				bot.connection.ctcp(ctcptype, event.target(), ctcptext)
				return # done

			elif event.eventtype() == "ctcp_reply":
				bot.connection.ctcp_reply(event.target(), event.arguments()[0])
				return # done

		if event.eventtype() == "continue":
			return
