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

"""hi.py - dummy function that says Hi """

handler_list=["kbbeep"]

from moobot_module import MooBotModule
from handler import Handler


class kbbeep(MooBotModule):
	def __init__(self):
		self.regex="\a"
		self.priority = -30
		self.type = Handler.GLOBAL

	def handler(self, **args):
		"""A dummy handler we used for testing -- this is the first handler we wrote"""
		from irclib import nm_to_h, nm_to_n, Event
		print "someone beeped!"
		result = [ 
		Event("internal", "send_raw", "", ["send_raw", "mode %s +b *!*@%s" % (args["channel"], nm_to_h(args["source"]) ) ] )  , 
		Event("internal", "send_raw", "", ["send_raw", "kick %s %s :don't beep." % (args["channel"], nm_to_n(args["source"]))]) 
		]
		return result
