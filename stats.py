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

""" stats.py - hehstats, lolstats, etc """
from moobot_module import MooBotModule
from moobot import Handler
handler_list = ["increment", "stats", "reset_stats", "set_stats", "find"]

class increment(MooBotModule):
	def __init__(self):
		self.regex = "^(\.\.\.|hehe?|h[a4]w|bah|lol|moo|[:;]\))$"
		self.type = Handler.GLOBAL
		self.priority = 3

	def handler(self, **args):
		"""when somebody says something handled by this module, their
		count for that thing is incremented by this function"""
		from irclib import Event
		import database
		import string
		from irclib import nm_to_n
		keyword = args["text"]
		keyword = keyword[string.find(keyword, " ")+1:]
		results=database.doSQL("select counter from stats where nick = '" + nm_to_n(args["source"]) + "' and type = '" + keyword + "'")
		if len(results) == 0:
			database.doSQL("insert into stats values( '" + nm_to_n(args["source"]) + "', '" + keyword + "', 0)")
			results=database.doSQL("select counter from stats where nick = '" + nm_to_n(args["source"]) + "' and type = '" + keyword + "'")
		database.doSQL("update stats set counter = counter + 1 where nick = '" + nm_to_n(args["source"]) + "' and type= '" +keyword+"'")
		target=args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
		return Event("continue", "", target, [ "" ])

class stats(MooBotModule):
	def __init__(self):
		self.regex = "^(\.\.\.|hehe?|lol|bah|h[a4]w|moo|[:;]\))stats$"

	def handler(self, **args):
		"""when you say, for instance, hehstats, this function is 
		called and reports your hehstats."""
		import database
		import string
		from irclib import nm_to_n, Event

		target = self.return_to_sender(args)

		# Grab which type of stat we are trying to get
		# 
		# Split into separate words, take the first word (which should be
		# "<type>stats"), and chop off the last five letters ("stats")
		type = args["text"].split(" ")[1][:-5]
		
		#type = args["text"]
		#type = type[string.find(type, " ")+1:]
		#type = type[:len(type)-5]
		
		# Grab the top 3
		records=database.doSQL("select nick, counter from stats where type = '" + type  + "' order by counter desc limit 3")
		stat=0
		text = "Top 3 \"" + type +"\"ers"
		addUser = 1
		while stat < 3 and stat < len(records) :
			text = text + "   " + str(stat+1) + ")  " + records[stat][0] + ": " + str(int(records[stat][1]))
			# If the user is in the top 3, no need to add their stats to the
			# end
			if records[stat][0] == nm_to_n(args["source"]):
				addUser = 0
			stat=stat+1

		# Grab the total stats and prepend them to the top 3
		records=database.doSQL("select sum(counter) from stats where type='" + type + "'")
		total = records[0][0]
		text = '"' + type + '" said a total of ' + str(total)[:-2] + ' times. ' + text

		# If we need to add the user's stats on, grab them and add them
		if addUser == 1:
			# Find the user's place in the grand scheme
			# 
			# First grab their totals
			usercount = database.doSQL("select counter from stats where type = '" + type + "' and nick = '" + nm_to_n(args["source"]) + "'")
			if len(usercount):
				usercount = usercount[0][0]
			else:
				usercount = 0
			# Then see how many have stats
			query = "select count(nick) from stats where type='" + type + "'"
			total_users = database.doSQL(query)[0][0]
			# And lastly, see how many have better stats
			query = "select count(nick) from stats where type='" + type + \
				"' and counter > " + str(usercount)
			beaten_by = database.doSQL(query)[0][0] + 1


			text += " -- You have said \"" + type +"\" " + \
				`int(usercount)` + " times, " + nm_to_n(args["source"]) + "."
				
			if usercount != 0:
				text += "  You rank " + str(beaten_by) + " out of " + \
				str(total_users) + "."

		return Event("privmsg", "", target, [ text ])

class reset_stats(MooBotModule):
	def __init__(self):
		self.regex="^(\.\.\.|hehe?|lol|bah|moo|h[a4]w|karma|[:;]\))reset .+$"

	def handler(self, **args):
		"""deletes a specific stat for a given user"""
		import database
		import string
		import priv
		from irclib import Event
		from irclib import nm_to_n
	
		target = self.return_to_sender(args)
	
		type = args["text"].split()[1]
		type = type[:len(type)-5]
		who = args["text"].split()[2]
		if priv.checkPriv(args["source"], "reset_stats_priv") == 0:
			return Event("privmsg", "", target, [ "You aren't allowed to do that" ])
		
		print type, who
		records=database.doSQL("delete from stats where type = '" + type  + "' and nick = '" + who + "'")
		return Event("privmsg", "", target, [ "Reset " + who + "'s " + type + " stats." ])

class set_stats(MooBotModule):
	def __init__(self):
		self.regex="^(\.\.\.|hehe?|lol|bah|moo|h[a4]w|karma|[:;]\))set .+ -?\d+$"

	def handler(self, **args):
		"""Set someone's stats to a specific number"""
		import priv, database
		from irclib import Event
		target = self.return_to_sender(args)

		# Remove bot name
		text = args["text"].split()[1:]
		type = text[0][:-3]	# First element is the stat type
		names = text[1:-1]	# All but the first and last elements are names
		count = text[-1]	# Last one is the number to set it to


		# Check privs
		if priv.checkPriv(args["source"], "reset_stats_priv") == 0:
			return Event("privmsg", "", target, [ "You aren't allowed to do that" ])

		# Since some of these may already be set, but some may not, we can't
		# simply use "update".  The easiest way to do it is to delete all of
		# them and re-insert them.
		#
		# Delete first
		query = "delete from stats where type='" + \
			type + "' and "
		for name in names:
			query += "nick='" + name + "' or "
		# Remove the last " or "
		query = query[:-4]
		# Do it to it
		database.doSQL(query)
		#
		# Now re-insert one by one
		# FIXME: is there a way to do this all in one - like build a huge
		# query and then just make one call?
		for name in names:
			query = "insert into stats(counter, nick, type) values(" \
				+ count + ", '" + name + "', '" + type + "')"
			database.doSQL(query)
		
		msg = "Set " + type + " to " + str(count) + " for: "
		for name in names:
			msg += name + ", "
		# Remove the last ", "
		msg = msg[:-2]
		return Event("privmsg", "", target, [ msg ])

class find(MooBotModule):
	def __init__(self):
		self.regex = "^(stat|hehe?|lol|bah|moo|h[a4]w|karma|[:;]\))find .+$"

	def handler(self, **args):
		"""Search for a certain string having either a given stat or any stat
		at all ("statfind foo")"""
		import database
		from irclib import Event
		target = self.return_to_sender(args)

		# Remove bot name
		text = args["text"].split()[1:]
		stat = text[0][:-4]		# First word, strip "find" from the end
		name = text[1]

		if stat == "stat":
			# Build the message prefix
			msg = "Matching for any stat, matching on '" + name + "' "
			# Get the number first
			query = "select count(counter) from stats where nick " \
				+ "like '%" + name + "%'"
			count = database.doSQL(query)[0][0]

			if count > 15:
				msg += "(" + str(count) + " found, 15 shown): "
			else:
				msg += "(" + str(count) + " found): "
			# Now the actual nicks and types
			query = "select nick, type from stats where nick " \
				+ "like '%" + name + "%' limit 15"
			results = database.doSQL(query)
			for tuple in results:
				msg += tuple[0] + " [" + tuple[1] + "] ;; "
			# Remove the last " ;; "
			if count != 0:
				msg = msg[:-4]
			return Event("privmsg", "", target, [msg])
		else:
			# Build the message prefix
			msg = "Matching " + stat + "stats for '" + name + "' "
			# Get the number first
			query = "select count(counter) from stats where nick " \
				+ "like '%" + name + "%' and type='" + stat + "'"
			count = database.doSQL(query)[0][0]

			if count > 15:
				msg += "(" + str(count) + " found, 15 shown): "
			else:
				msg += "(" + str(count) + " found): "
			# Now the actual nicks for that type
			query = "select nick from stats where nick like " \
				+ "'%" + name + "%' and type='" + stat + "' limit 15"
			results = database.doSQL(query)
			for tuple in results:
				msg += tuple[0] + " ;; "
			# Remove the last " ;; "
			if count != 0:
				msg = msg[:-4]
			return Event("privmsg", "", target, [msg])
