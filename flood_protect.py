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

"""flood_protect.py - intercepts bot flooding """

handler_list=["flood_protect"]

from moobot_module import MooBotModule
from moobot import Handler
import priv
import time

class flood_protect(MooBotModule):
	class message:
		time = 0
		message = ""

	def __init__(self):
		self.regex="^.*$"
		self.priority=-18
		self.type = Handler.GLOBAL
		self.messages = {}

	def handler(self, **args):
		from irclib import Event
		if args["source"] in self.messages.keys():
			if self.messages[args["source"]].message == args["text"] and \
			self.messages[args["source"]].time + 5 >= time.time() and \
			priv.checkPriv(args["source"], "flood_priv") == 0:
				self.messages[args["source"]].time = time.time()
				print "ignoring duplicate message"
				return Event("do nothing", "", "", [ ])

			self.messages[args["source"]].message = args["text"]
			self.messages[args["source"]].time = time.time()
		else:
			temp = self.message()
			temp.time = time.time();
			temp.message = args["text"]
			self.messages[args["source"]] = temp
				
		return Event("continue", "", "", [  ])
