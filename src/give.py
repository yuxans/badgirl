#!/usr/bin/env python

# Copyright (c) 2002 Daniel DiPaolo, et. al.
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
handler_list = ["give"]

class give(MooBotModule):
	def __init__(self):
		self.regex = "^give .+$"

	def handler(self, **args):
		import re
		from irclib import Event, nm_to_n

		who = "".join(args["text"].split(" ")[2:])
		name_w_spaces = " " + nm_to_n(args["source"]) + " "
		text = re.sub("(\sme\s|\sme$|^me\s)", name_w_spaces, who)
		text = re.sub("(^\s+|\s+$)", "", text)
		text = "gives "+text

		result = Event("action", "", self.return_to_sender(args), [text])
		return result
