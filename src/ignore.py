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

"""ignore.py - handles ignoring abusive users """
handler_list=["ignorePublicPattern", "ignorePublic", "ignorePrivate"]

from moobot_module import MooBotModule
from moobot import Handler

class ignorePublicPattern(MooBotModule):
	type = Handler.GLOBAL
	regex = r"^(\[Request\] )"
	stripColor = True
	priority = -20

	def handler(self, **args):
		self.Debug("ignored " + args['text'])
		return self.Event("do nothing", "", "" , [])

class ignore(MooBotModule):
	def __init__(self):
		self.regex = ".*"
		self.priority = -19

	def handler(self, **args):
		"""returns a continue if the user is not to be ignored, otherwise
		returns a "do nothing" handler"""
		import priv
		from irclib import Event
		if priv.checkPriv(args["source"], "notalk_priv") != 0 and priv.checkPriv(args["source"], "all_priv") == 0:
			self.debug("ignoring message by " + args["source"])
			return Event("do nothing", "", "" , [ ])
		return Event("continue", "", "" , [])

class ignorePublic(ignore):
	def __init__(self):
		ignore.__init__(self)
		self.type = Handler.GLOBAL

class ignorePrivate(ignore):
	def __init__(self):
		ignore.__init__(self)
		self.type = Handler.LOCAL


