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

"""module_handling.py - used to load/unload/reload modules"""

from moobot_module import MooBotModule
handler_list = ["reload", "load", "unload"]


class reload(MooBotModule):
	""" returns events to unload and load specified modules"""
	def __init__(self):
		self.regex="^reload\s?(.+)?$"
		self.priority=-20

	def handler(self, **args):
		import priv, string
		from irclib import Event
		module_list = []
		for module in args["text"].split()[2:]:
			module_list.append(module)
		if priv.checkPriv(args["source"], 'module_priv') != 0:
			return [Event("internal", "", "", [ "unload" ] + module_list),
				Event("internal", "", "", [ "load" ] + module_list), 
				Event("privmsg", "", self.return_to_sender(args), [ "loading "  + string.join(module_list)] )]
		else:
			return Event("privmsg", "", self.return_to_sender(args), [ "that requires module_priv." ])

class load(MooBotModule):
	""" returns events load specified modules"""
	def __init__(self):
		self.regex="^load\s(.+)?$"
		self.priority=-20

	def handler(self, **args):
		import priv, imp, string
		from irclib import Event
		module_list = []
		for module in args["text"].split()[2:]:
			module_list.append(module)
		fail = 0
		failedMessage = "Unable to find : "
		if priv.checkPriv(args["source"], 'module_priv') != 0:
			# check if they all exist first
			for name in module_list:
				try:
					fp, pathname, description = imp.find_module(name)
					fp.close()
				except:
					fail = 1
					failedMessage += name +" "
			if (fail == 1):
				return Event("privmsg", "", self.return_to_sender(args), [ failedMessage ])

			else:
				return [Event("internal", "", "", [ "load" ] + module_list), Event("privmsg", "", self.return_to_sender(args), [ "loading "  + string.join(module_list)] )]
		else:
			return Event("privmsg", "", self.return_to_sender(args), [ "that requires module_priv." ])
class unload(MooBotModule):
	""" returns events to unload specified modules"""
	def __init__(self):
		self.regex="^unload\s(.+)?$"
		self.priority=-20

	def handler(self, **args):
		import priv
		from irclib import Event
		module_list = []
		for module in args["text"].split()[2:]:
			module_list.append(module)
		if priv.checkPriv(args["source"], 'module_priv') != 0:
			return Event("internal", "", "", [ "unload" ] + module_list)
		else:
			return Event("privmsg", "", self.return_to_sender(args), [ "that requires module_priv." ])
