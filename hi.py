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

handler_list=["hi"]

from moobot_module import MooBotModule


class hi(MooBotModule):
	def __init__(self):
		self.regex="^hi$"

	def handler(self, **args):
		"""A dummy handler we used for testing -- this is the first handler
		we wrote"""
		from irclib import Event
		return Event("privmsg", "", self.return_to_sender(args), [ "hi" ])
