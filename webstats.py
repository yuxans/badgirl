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

"""webstats.py - capture stats for display on the web and produce web stat
page"""

from moobot_module import MooBotModule
from moobot import Handler
handler_list = ["count_speak_times", "get_quote"]

class count_speak_times(MooBotModule):
	def __init__(self):
		self.regex=".*"
		self.priority = -15
		self.type = Handler.GLOBAL

	def handler(self, **args):
		"""Simply increments a counter in the database that keeps track of how
		many times a person has spoken.  Also stores a random quote from the
		person (basically 10% chance a given quote is going to be chosen for the
		"random quote" in the database."""
		import database, time, random, string
		from irclib import Event, nm_to_n
	
		# Get nick and quote text
		nick = nm_to_n(args["source"]).lower()
		quote = self.sqlEscape(string.joinfields(args["text"].split()[1:]))
		channel = args["channel"].lower()
		if args["type"] == "privmsg": target = nm_to_n(args["source"])
		else: target = args["channel"]
		# Increment counter for that nick if it exists, otherwise insert into DB
		query = "select count, quote_time from webstats where nick='" + \
			nick + "' and" + " channel='" + channel + "'"
		result = database.doSQL(query)
		response = []
		if result == []:
			# Insert their first quote as their random quote and set count to 1
			query = "insert into webstats(nick, channel, count, quote," \
				+ " quote_time) values('" + nick + "', '" + channel + "', 1, '" \
				+ quote + "', " + str(int(time.time())) + ")"
			database.doSQL(query)
#			response.append(Event("action", "", target, \
#				["jots down a new quote for " + nick]))
		else:
			import time
			# Get the current count and increment it
			new_count = int(result[0][0]) + 1
			# Get the current quote's date
			quote_time = int(result[0][1])
			curr_time = int(time.time())
			secs_elapsed = curr_time - quote_time
			days_elapsed = secs_elapsed / 24 / 60 / 60
			# We don't want quotes that are under 8 letters, they are boring.
			#
			# We also don't want quotes of less than 4 words, also usually
			# boring as well.
			#
			# We also don't want stale quotes, so use the number of days since
			# the current quote times some constant to pick the quote
			if (random.randrange(new_count) < (days_elapsed * 10)) and \
				len(quote) > 8 and \
				len(quote.split()) >= 4:
				query = "update webstats set count=" + str(new_count) \
					+ ", quote='" + quote + "', quote_time=" \
					+ str(int(time.time())) + " where nick='" + nick + "'" \
					+ " and channel='" + channel + "'"
				database.doSQL(query)
				if new_count > 10:
					response.append(Event("continue", "", target, [""]))
			else:
				query = "update webstats set count=" + str(new_count) + " where " \
				+ "nick='" + nick + "' and channel='" + channel + "'"
				database.doSQL(query)
			
		response.append(Event("continue", "", target, [""]))
		return response
	
class get_quote(MooBotModule):
	def __init__(self):
		self.regex="^q(uo|ou)te\s+.+"

	def handler(self, **args):
		from irclib import Event, nm_to_n
		import database, string
		nick = args["text"].split()[2].lower() # name
		nick = string.replace(nick, "\\", "\\\\")
		nick = string.replace(nick, "'", "\\'")
		record = database.doSQL("select * from webstats where nick = '" + nick + "' and channel = '" + args["channel"] + "'")
		quote = ""
		if record:
			self.debug(record)
			quote = "<" + self.str(record[0][0]) + "/" + self.str(record[0][4]) + "> " + self.str(record[0][2])
		else:
			quote = "No quote available from " + args["text"].split()[2]
		if args["type"] == "privmsg":
			target = nm_to_n(args["source"])
		else:
			target = args["channel"]
	
		return Event("privmsg", "", target, [quote])

