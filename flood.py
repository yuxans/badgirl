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

handler_list=["flood"]

from moobot_module import MooBotModule


class flood(MooBotModule):
	def __init__(self):
		self.regex="^flood .+"

	def handler(self, **args):
		from irclib import Event
		
		target = args["text"].split()[2]
		
		msg = "SPAM!! " * 73 
		msg = msg + "\n"
		msg = msg * 4
		
		return Event("privmsg", "", target, [ msg ])
