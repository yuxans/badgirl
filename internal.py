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

"""internal.py - moobot internal functions

This module [will have] functions for such things as channel joins and parts,
(de)opping, et cetera.
"""
handler_list=["join", "nick", "part", "list_modules", "send_raw", "kick"]

from moobot_module import MooBotModule


class join(MooBotModule):
	def __init__(self):
		self.regex = "^join .*"

	def handler(self, **args):
		"""handles "join" commands with priv checking"""
		from irclib import Event
		import priv
		if priv.checkPriv(args["source"], "join_priv") == 0:
			target = args["channel"]
			if args["type"] == "privmsg":
				from irclib import nm_to_n
				target=nm_to_n(args["source"])
			return Event("privmsg", "", target, [ "You do not have permission to do that." ])

		import string
		channel = args["text"]
		channel = channel[string.find(channel, " ")+1:]
		channel = channel[string.find(channel, " ")+1:]
		result = Event("internal", "", channel, [ "join" ] )
		return result

class nick(MooBotModule):
	def __init__(self):
		self.regex = "^nick .*"

	def handler(self, **args):
		"handles \"join\" commands with priv checking"
		from irclib import Event
		import priv
		if priv.checkPriv(args["source"], "nick_priv") == 0:
			target = args["channel"]
			if args["type"] == "privmsg":
				from irclib import nm_to_n
				target=nm_to_n(args["source"])
			return Event("privmsg", "", target, [ "You do not have permission to do that." ])

		import string
		channel = args["text"]
		channel = channel[string.find(channel, " ")+1:]
		channel = channel[string.find(channel, " ")+1:]
		result = Event("internal", "", channel, [ "nick" ] )
		return result

class join_nopriv(MooBotModule):
	def __init__(self):
		self.regex = "^join .*"

	def handler(self, **args):
		"""handles "join" commands without priv checking"""
		from irclib import Event
		target = args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
		import string
		print "join"
		channel = args["text"]
		channel = string.joinfields(channel.split(" ")[2:])
		result = Event("internal", "", channel, [ "join" ] )
		return result

class part(MooBotModule):
	def __init__(self):
		self.regex = "^part .*"

	def handler(self, **args):
		"""handles "part" commands with priv checking"""
		from irclib import Event
		import priv
		if priv.checkPriv(args["source"], "part_priv") == 0:
			target = args["channel"]
			if args["type"] == "privmsg":
				from irclib import nm_to_n
				target=nm_to_n(args["source"])
			return Event("privmsg", "", target, [ "You do not have permission to do that." ])
		import string
		channel = args["text"]
		channel = channel[string.find(channel, " ")+1:]
		channel = channel[string.find(channel, " ")+1:]
		result = Event("internal", "", channel, [ "part" ] )
		return result

class part_nopriv(MooBotModule):
	def __init__(self):
		self.regex="^part .+"

	def handler(self, **args):
		"""handles "part" commands without priv checking"""
		from irclib import Event
		target = args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
		import string
		print "part"
		channel = args["text"]
		channel = string.joinfields(channel.split(" ")[2:])
		result = Event("internal", "", channel, [ "part" ] )
		return result

class kick(MooBotModule):
	def __init__(self):
		self.regex = "^kick #.+ .+"

	def handler(self, **args):
		"""handles "kick" commands -- need to implement permission checking on this"""
		from irclib import Event
		import priv
		if priv.checkPriv(args["source"], "kick_priv") == 0:
			target = args["channel"]
			if args["type"] == "privmsg":
				from irclib import nm_to_n
				target=nm_to_n(args["source"])
			return Event("privmsg", "", target, [ "You do not have permission to do that." ])
		import string
		user = args["text"]
		user = user[string.find(user, " ")+1:]
		user = user[string.find(user, " ")+1:]
		result = Event("internal", "", string.split(user)[1], [ "kick" ,string.split(user)[0]] )
		return result

class list_modules(MooBotModule):
	def __init__(self):
		self.regex = "^MODULES?\s+.*"
	
	def handler(self, **args):
		"Lists modules using an internal"
		from irclib import Event, nm_to_n
		target=nm_to_n(args["source"])
		# Strip name and 'module(s)' from text
		from string import joinfields
		msg = joinfields(args["text"].split(" ")[2:])
		return Event("internal", "", target, [ "modules", msg ])

class send_raw(MooBotModule):
	def __init__(self):
		self.regex = "^send raw\s+.*"
	
	def handler(self, **args):
		import priv, string
		from irclib import Event
		if (priv.checkPriv(args["source"], "all_priv") == 0):
			return Event("privmsg", "", self.return_to_sender(args), ["You can't do that!"])

		print string.split(args["text"], " ", 3)[3]
		return Event("internal", "send_raw", "", ["send_raw", string.split(args["text"], " ", 3)[3] ])
