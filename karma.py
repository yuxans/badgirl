#!/usr/bin/env python

# Copyright (c) 2002 Daniel DiPaolo
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

"""karma.py -- Moobot Karma Handlers

Includes functionality for viewing/increasing/decreasing karma
"""
handler_list = ["karma"]
from moobot_module import MooBotModule

class karma(MooBotModule):
	"Either increases, decreases, or lists the karma"
	def __init__(self):
		self.regex = "(^karma( .+$)?$|^\w+(\+\+|\-\-)$)"

	def handler(self, **args):
		import database
		from irclib import Event, nm_to_n
		
		# Set the target as either the person or the channel
		target = self.return_to_sender(args)
		
		orig_msg = args["text"]
		# Strip bot name
		orig_msg = orig_msg.split()[1:]
	
		# Now determine if we need to list karma or increment/decrement it,
		# which we check by seeing if the first word is "karma"
		msg = ""
		if orig_msg[0] == "karma":
			# If they just say "karma", self.debug(the top 3, the bottom 3, and)
			# the requester's karma
			if len(orig_msg) == 1:
				top = "Top 3 Karma -"
				# Top 3
				query = "select counter, nick from stats where type='karma'" \
					+ " order by counter desc limit 3"
				record = database.doSQL(query)
				for i in range(len(record)):
					# i goes from 0 to 2 (hopefully)
					top += " " + str(i+1) + ") " + record[i][1] + ": " \
						+ self.str(record[i][0]) + ";"
				top += "\n"
				# Bottom 3
				bot = "Bottom 3 Karma -"
				query = "select counter, nick from stats where type='karma'" \
					+ " order by counter asc limit 3"
				record = database.doSQL(query)
				for i in range(len(record)):
					bot += " " + str(i+1) + ") " + record[i][1] + ": " \
						+ self.str(record[i][0]) + ";"
				bot += "\n"
				# Requesters
				import irclib
				name = irclib.nm_to_n(args["source"])
				self.debug(name)
				query = "select counter from stats where nick='" + name + "' and type='karma'"
				record = database.doSQL(query)		
				if len(record) != 0:
					req = name + ": " + self.str(record[0][0])
				else:
					req = ""

				return Event("privmsg", "", target, [ top + bot + req ])
			else:
				names = orig_msg[1:]
				for name in names:
					query = "select counter from stats where nick='" + name + "' and type='karma'"
					record = database.doSQL(query)		
					if len(record) != 0:
						msg += name + ": " + self.str(record[0][0]) + " ;; "
					else:
						msg += name + " has no karma stats" + " ;; "
				msg = msg[:-4]
				return Event("privmsg", "", target, [ msg ])
		else:			
			name = orig_msg[0][:-2]
			operator = orig_msg[0][-2:]
			if operator == "++" or operator == "--":
				if args["type"] == "privmsg":
					return Event("privmsg", "", self.return_to_sender(args), ["Karma must be done in public."])
					
				# First check to see if their stats exist
				query = "select counter from stats where nick='" + name + "' and type='karma'"
				record = database.doSQL(query)
				if len(record) != 0:
					if operator == "++":
						query = "update stats set counter="+ self.str(record[0][0]) +"+1 where nick='" + name + "' and type='karma'"
						database.doSQL(query)
					else:
						query = "update stats set counter="+ self.str(record[0][0]) +"-1 where nick='" + name + "' and type='karma'"
						database.doSQL(query)
				else:
					if operator == "++":
						query = "insert into stats(nick, counter, type) values('" + name + "', 1, 'karma')"
						database.doSQL(query)
					else:
						query = "insert into stats(nick, counter, type) values('" + name + "', -1, 'karma')"
						database.doSQL(query)
				return Event("do nothing", "", target, [""])
			else:
				# Shouldn't ever get here, but in case we do...
				self.debug("Shouldn't be here! -", args["text"])
