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

"""rejoin.py -- rejoin when kicked """

handler_list=["rejoin"]

from moobot_module import MooBotModule


class rejoin(MooBotModule):
	def __init__(self):
		self.type="kick"

	def handler(self, **args):
		"""when the bot is kicked, it'll rejoin if the channel from which
		it was kicked is in the data table with type "rejoinchan"""
		from irclib import Event
		import database
		bot = args["ref"]()
		e = args["event"]
		channel = e.target()
		count = database.doSQL("select count(data) from data where type = 'rejoinchan' and data = '%s'" % (channel)) # check if we rejoin this channel
		if e.arguments()[0] == bot.connection.get_nickname() and count[0][0] > 0:
			result = Event("internal", "", channel, [ "join" ] )
			return result
		else:
			return Event("continue", "", "", [""])
