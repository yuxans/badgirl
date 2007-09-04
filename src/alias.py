#!/usr/bin/env python

# Copyright (c) 2002 Phil Gregory
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

"""alias.py - Function to keep track of nick aliases."""

handler_list=["whois_cmd", "alias_nickchange"]
from moobot_module import MooBotModule


class whois_cmd(MooBotModule):
	def __init__(self):
		self.regex="^whois ."

	def handler(self, **args):
		from irclib import Event

		nick = args["text"].split(" ")[2]
		realnick = whois(nick)
		return Event("privmsg", "", self.return_to_sender(args),
			     [nick + " is " + realnick])


class alias_nickchange(MooBotModule):
	def __init__(self):
		self.type = "nick"
		self.regex="."
		self.priority = -20

	def handler(self, **args):
		from irclib import Event
		import database

		oldnick = args["event"].source().lower()
		newnick = args["event"].target().lower()
		oldrealnick = whois(oldnick)
		newrealnick = whois(newnick)

		if (oldrealnick != newrealnick):
			oldrealtype = database.doSQL("SELECT type FROM alias "+\
						     "WHERE nick = '" + \
						     oldrealnick + "'")[0][0]
			newrealtype = database.doSQL("SELECT type FROM alias "+\
						     "WHERE nick = '" + \
						     newrealnick + "'")[0][0]
			if (oldrealtype == "cached" and \
			    newrealtype == "cached"):
				database.doSQL("UPDATE alias " + \
					       "SET type = 'nickchange' " + \
					       "WHERE nick = '" + oldrealnick + "'")
				database.doSQL("UPDATE alias " + \
					       "SET type = 'nickchange', " + \
					       "realnick = '" + oldrealnick + \
					       "' " + \
					       "WHERE nick = '" + newnick + "'")
			elif (oldrealtype == "cached"):
				database.doSQL("UPDATE alias " + \
					       "SET type = 'nickchange', " + \
					       "realnick = '" + newrealnick + \
					       "' " + \
					       "WHERE nick = '" + oldnick + "'")
			elif (newrealtype == "cached"):
				database.doSQL("UPDATE alias " + \
					       "SET type = 'nickchange', " + \
					       "realnick = '" + oldrealnick + \
					       "' " + \
					       "WHERE nick = '" + newnick + "'")
					       

		return Event("continue", "", "", [  ])


def whois(fullnick):
	import database

	fullnick = fullnick.lower()
	nick = fullnick.split("!")[0]

	line = database.doSQL("SELECT realnick FROM alias " + \
			      "WHERE nick = '" + nick + "'")
	if (len(line) > 0):
		if (line[0][0] == nick):
			return line[0][0]
		else:
			return whois(line[0][0])

	line = database.doSQL("SELECT regex, realnick FROM aliasregex")
	import re
	# Split into two similar for loops for speed reasons.
	if (fullnick.find("!") and fullnick.find("@")):
		for item in line:
			if (not item[0].find("!") and \
			    not item[0].find("@")):
				item[0] += "![^@]+@.+"
			elif (not item[0].find("!")):
				item[0] = "[^!]+!" + item[0]
			elif (not item[0].find("@")):
				item[0] += "@.+"
			if (re.search("^" + item[0] + "$", fullnick)):
				database.doSQL("INSERT INTO alias " + \
					       "(nick, realnick, type) " + \
					       "VALUES ('" + nick + "', '" + \
					       item[1] + "', 'regex')")
				return item[1]
	else:
		for item in line:
			if (re.search("^" + item[0] + "$", nick)):
				database.doSQL("INSERT INTO alias " + \
					       "(nick, realnick, type) " + \
					       "VALUES ('" + nick + "', '" + \
					       item[1] + "', 'regex')")
				return item[1]

	# Default.
	database.doSQL("INSERT INTO alias (nick, realnick, type) " + \
		       "VALUES ('" + nick + "', '" + nick + "', 'cached')")
	return nick
