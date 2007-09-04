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

""" seen.py - logs who was where when """
from moobot_module import MooBotModule
from moobot import Handler
handler_list=["seen", "see_privmsg", "see_action", "see_part", "see_quit",
	      "see_join", "see_nick"]


class see_privmsg(MooBotModule):
	def __init__(self):
		self.regex="."
		self.priority=-50
		self.type = Handler.GLOBAL

	def handler(self, **args):
		"""when somebody says something, their record is added
		or updated."""
		add_seen(args["source"], "privmsg", args["text"])
	
		from irclib import Event
		return Event("continue", "", "", [ "" ])
	

class see_action(MooBotModule):
	def __init__(self):
		self.regex="."
		self.priority=-50
		self.type = "ctcp"

	def handler(self, **args):
		"""Updates the seen table for actions."""

		e = args["event"]
		if (e.arguments()[0] == "ACTION"):
			add_seen(e.source(), "action", e.arguments()[1])
		
		from irclib import Event
		return Event("continue", "", "", [ "" ])
	

class see_part(MooBotModule):
	def __init__(self):
		self.regex="."
		self.priority=-50
		self.type = "part"

	def handler(self, **args):
		"""Updates the seen table for channel partings."""

		e = args["event"]
		if (e.arguments()):
			add_seen(e.source(), "part", e.arguments()[0])
		else:
			add_seen(e.source(), "part", "")
		
		from irclib import Event
		return Event("continue", "", "", [ "" ])
	

class see_quit(MooBotModule):
	def __init__(self):
		self.regex="."
		self.priority=-50
		self.type = "quit"

	def handler(self, **args):
		"""Updates the seen table for IRC quits.  Only records quit
		events that are definitely the result of user action."""
		e = args["event"]
		if (extract_quit_message(e.arguments()[0]) != ""):
			add_seen(e.source(), "quit", e.arguments()[0])
		
		from irclib import Event
		return Event("continue", "", "", [ "" ])
	

class see_join(MooBotModule):
	def __init__(self):
		self.regex="."
		self.priority=-50
		self.type = "join"

	def handler(self, **args):
		"""Updates the seen table for channel joins.  Joins are only
		recorded when the previous event for the nick was a part or
		quit.  (If it's not, then the part or quit may have been
		automatic, so this join may be automatic."""
		import database
		from irclib import nm_to_n
		
		e = args["event"]
		line = database.doSQL("SELECT type FROM seen WHERE nick = '" + \
				      escape_quotes(nm_to_n(e.source())) + "'")
		if (len(line) > 0 and line[0][0] in ["quit", "join"]):
			add_seen(e.source(), "join", "")
		
		from irclib import Event
		return Event("continue", "", "", [ "" ])
	

class see_nick(MooBotModule):
	def __init__(self):
		self.regex="."
		self.priority=-50
		self.type = "nick"

	def handler(self, **args):
		"""Updates the seen table for nick changes."""

		e = args["event"]
		add_seen(e.source(), "nick", e.target())
		
		from irclib import Event
		return Event("continue", "", "", [ "" ])
	

class seen(MooBotModule):
	def __init__(self):
		self.regex = "^seen ."

	def handler(self, **args):
		"""Report when someone was last seen."""
		import database
		from alias import whois

		result = ""

		nick = " ".join(args["text"].split()[2:])
		safenick = escape_quotes(nick.lower())
		line = database.doSQL("SELECT nick, time, message, type " + \
				      "FROM seen WHERE nick = '" + safenick + \
				      "'")
		if (len(line) == 0):
			seentime = 0
			joiner = "However, "
			result += "I don't think I've ever seen " + nick + ".\n"
		else:
			seentime = int(line[0][1])
			joiner = "Also, "
			result += makeseenline("", line)

		realnick = escape_quotes(whois(nick))
		line = database.doSQL("SELECT seen.nick, seen.time, seen.message, seen.type FROM seen, alias WHERE seen.time > " + str(seentime) + " AND seen.nick = alias.nick AND alias.realnick = '" + realnick + "' ORDER BY seen.time DESC LIMIT 1")
		if (len(line) > 0):
			result += makeseenline(joiner, line)
		
		from irclib import Event
		return Event("privmsg", "", self.return_to_sender(args), [ result ])


def  escape_quotes(text):

	text = text.replace("\\", "\\\\")
	text = text.replace("'", "\\'")
	return text


def add_seen(hostmask, type, message):
	from irclib import nm_to_n
	from alias import whois
	import database, time
	
	message = escape_quotes(message)
	nick = escape_quotes(nm_to_n(hostmask)).lower()
	whois(nick)

	if len(database.doSQL("SELECT * FROM seen " + \
			      "WHERE nick = '" + nick + "'")) == 0:
		database.doSQL("INSERT INTO seen " + \
			       "(nick, hostmask, time, message, type)" + \
			       "VALUES('" + nick + "', '" + hostmask  + \
			       "', " + str(int(time.time())) + ", '" + \
			       message + "', '" + type + "')")
	else:
		database.doSQL("UPDATE seen " + \
			       "SET hostmask = '" + hostmask + "', time = '" + \
			       str(int(time.time())) + "', message = '" + \
			       message + "', type = '" + type + "' " + \
			       "WHERE nick = '" + nick + "'")


def t2s_add_unit(timediff, timelist, period, name):
	num_units = 0
	if (timediff >= period):
		num_units = int(timediff / period)
		timelist.append(str(num_units) + " " + name)
		if (num_units != 1):
			timelist[len(timelist) - 1] += "s"
	return timediff - num_units * period


def time2str(timeticks):
	import time

	timelist = []
	timediff = (time.time() - timeticks)
	# Have to do this one ourselves because of the day handling at the end.
	if (timediff >= 31556952):  # one year, 365.2425 days
		timeamt = int(timediff / 31556952)
		timelist.append(str(timeamt) + " year")
		if (timeamt != 1):
			timelist[len(timelist) - 1] += "s"
		# Only subtract an integral number of days.
		timediff -= int(timeamt * 365.2425) * 86400
	timediff = t2s_add_unit(timediff, timelist, 86400, "day")
	timediff = t2s_add_unit(timediff, timelist, 3600, "hour")
	timediff = t2s_add_unit(timediff, timelist, 60, "minute")
	timediff = t2s_add_unit(timediff, timelist, 1, "second")

	if (len(timelist) == 0):
		timename = "0 seconds"
	elif (len(timelist) == 1):
		timename = timelist[0]
	elif (len(timelist) == 2):
		timename = " and ".join(timelist)
	else:
		timename = ", ".join(timelist[0:len(timelist)-1]) + \
			   ", and " + timelist[len(timelist)-1]

	return timename


def makeseenline(prefix, dbresult):
	import time, re

	away_msg = re.compile("^is (away|gone)")
	back_msg = re.compile("^(is back|ees home)")
	
	nick = dbresult[0][0]
	seentime = int(dbresult[0][1])
	message = dbresult[0][2]
	type = dbresult[0][3]
	if (type == "privmsg"):
		action = "last said something"
	elif (type == "action"):
		if (away_msg.search(message)):
			action = "went away"
			message = extract_away_message(message)
			if (message != ""):
				action += " (" + message + ")"
		elif (back_msg.search(message)):
			action = "came back"
		else:
			action = "last did something"
	elif (type == "nick"):
		action = "became " + message
	elif (type == "quit"):
		action = "quit"
		message = extract_quit_message(message)
		if (message != ""):
			action += " (" + message + ")"
	elif (type == "part"):
		action = "left"
		message = extract_quit_message(message)
		if (message != ""):
			action += " (" + message + ")"
	elif (type == "join"):
		action = "joined"
	else:
		action = "was somehow active"
				
	return prefix + nick + " " + action + " " + time2str(seentime) + \
	       " ago, at " + \
	       time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(seentime))+\
	       ".\n"


def extract_away_message(message):
	import re
	
	# Some common away prefixes.
	message = re.sub("^is (away|gone)([:,.] | - )*\s*", "", message)

	# Epic4/axur
	message = re.sub("^\x02\.\x02\. (.*) \.\x02\.\x02.*", "\1", message)

	# Other things I've seen.
	message = re.sub("^\s*\(\s*|\s*\)\s*$", "", message)
	message = re.sub("\s*\(l\/p!on\)\s*$", "", message)

	# Some messages are automatically-generated, so don't list those.
	# The "\x02\x02" is something I've seen used for an empty message.
	if (re.search("^(auto away|\x02\x02$)", message)):
		message = ""

	return message


def extract_quit_message(message):
	import re
	
	# OFTC's user quit messages are prefixed with "Quit: ".
	message = re.sub("^Quit:\s*", "", message)

	# Openproject's user quit messages are surrounded with double quotes.
	message = re.sub('^"|"$', "", message)

	# Ignore default client messages.
	if (re.search("(^(\x02BitchX\x02|\x02\[\x02BX\x02\]\x02|\[x\]chat|CGI:IRC|Client Exiting|ircII)|has no reason$)", message)):
		message = ""

	# Ignore messages that the user probably did not have an active hand in.
	if (re.search("^(read error|ping timeout|connection reset)", message, re.I)):
		message = ""


	return message
