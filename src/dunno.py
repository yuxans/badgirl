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

"""dunno.py - selects a random "I don't know" reply """

handler_list = ["dunno"]

from moobot_module import MooBotModule

class dunno(MooBotModule):
	def __init__(self):
		self.regex=".*"
		self.priority = 1000

	def handler(self, **args):
		"""grabs a random reply from the database"""
		from irclib import Event
		import database, string
		from irclib import nm_to_n
                # Different names; same function.  Sigh.
		if database.type == "pgsql":
			dunno_query = "select data from data where type='dunno' order " \
				+ "by random() limit 1"
		elif database.type == "mysql":
			dunno_query = "select data from data where type='dunno' order " \
				+ "by rand() limit 1"
		line = (database.doSQL(dunno_query) or [['dunno']])[0][0]

		line = string.replace(line, "WHO", nm_to_n(args["source"]))
		target = self.return_to_sender(args)
		return Event("privmsg", "", target, [ line ])
