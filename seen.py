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
handler_list=["update", "seen"]


class update(MooBotModule):
	def __init__(self):
		self.regex=".*"
		self.priority="-15"
		self.type = Handler.GLOBAL

	def handler(self, **args):
		"""when somebody says something, their record is added
		or updated.
		"""
		import database
		import string, time
		from irclib import nm_to_n
		from irclib import Event
		target = args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
	
		message = string.replace(args["text"], "\\", "\\\\")
		message = string.replace(message, "'", "\\'")
		message = string.join(message.split()[1:])
		if len(database.doSQL("select *  from seen where nick = '" + nm_to_n(args["source"]) + "'")) == 0:
			database.doSQL("insert into seen values('" + nm_to_n(args["source"]) + "', '" + args["source"]  + "', " + str(int(time.time())) + ", '" + message + "')")
		else:
			database.doSQL("update seen set hostmask = '" + args["source"] + "', time = '" + str(int(time.time())) + "', message = '" + message +"' where nick = '" + nm_to_n(args["source"]) + "'")
	
		return Event("continue", "", "", [ "" ])
	
class seen(MooBotModule):
	def __init__(self):
		self.regex = "^seen .+"

	def handler(self, **args):
		""" report when someone was last seen """
		import database
		import string, time
		from irclib import Event
		target = args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
		nick = string.join(args["text"].split()[2:])
		
		nick = escape_quotes(nick)
		if database.doSQL("select count(nick) from seen where nick = '" + nick + "'")[0][0] == 0:
			return Event("privmsg", "", target, ["nope."])
	
		records=database.doSQL("select * from seen where nick = '" + nick + "'")
	
		text = nick + " (" + records[0][1] + ") was last seen on " + time.ctime(records[0][2]) + " saying: \"" + records[0][3] + "\"."
		return Event("privmsg", "", target, [ text ])
	
def  escape_quotes(nick):
	import string
	nick = string.replace(nick, "\\", "\\\\")
	nick = string.replace(nick, "'", "\\'")
	return nick
