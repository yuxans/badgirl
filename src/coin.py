#!/usr/bin/env python

# Copyright (c) 2003 Phil Gregory
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

"""coin.py - flips a coin on demand"""

handler_list=["coin"]

from moobot_module import MooBotModule


class coin(MooBotModule):
	def __init__(self):
		self.regex="^coin"

	def handler(self, **args):
		"""If given a list of alternatives separated by 'or', picks
		from among them.  Otherwise picks either heads or tails from a
		virtual coin."""
		import random, re, string;
		from irclib import Event

		# Strip "botname: coin" off the front.
		str = string.join(args["text"].split()[2:])

		# Attempt some rudimentary first-to-second person changes.
		str = re.sub('\b([Ii]|[Mm][Ee])\b', 'you', str)
		str = re.sub('\b[Mm][Yy]\b', 'your', str)

		# Prepare the options for decision.
		str = re.sub('\?', '', str)
		options = re.split(',?\s+or\s+', str)
		if len(options) <= 1 or random.randint(1, 10) == 1:
			options = ["Heads!", "Tails!"]
			third = "Edge!?"
		elif len(options) == 2:
			third = "Both!"
		else:
			third = "All of them!"
		choice = random.choice(options)
		if (random.randint(1, 100) == 1):
			choice = third
		return Event("privmsg", "", self.return_to_sender(args),
			     [choice])
