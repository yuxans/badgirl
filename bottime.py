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

"""bottime.py - time-related modules """
from moobot_module import MooBotModule
handler_list=["cputime", "uptime"]

class cputime(MooBotModule):
	def __init__(self):
		self.regex = "^cputime$"

	def handler(self, **args):
		"""Reports CPU time usage for the Moobot"""
		from os import times
		from irclib import Event
		target=args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
		return Event("privmsg", "", target, [ "User time: " + str(times()[0]) + " seconds, system time: " + str(times()[1]) + " seconds.  Childrens' user time: " + str(times()[2]) + ", childrens' system time: " + str(times()[3])])

class uptime(MooBotModule):
	def __init__(self):
		import os, database, time
		self.regex = "^uptime$"
		self.ppid = os.getppid()

		database.doSQL("delete from data where type = 'uptime' and created_by != '" + str(os.getppid()) + "'");
		if len(database.doSQL("select * from data where type = 'uptime' and created_by ='" + str(os.getppid()) + "'")) == 0:
			database.doSQL("insert into data values('" + str(int(time.time())) + "', 'uptime', '" + str(os.getppid()) + "')")

	def handler(self, **args):
		import database, os, time
		from irclib import Event
		start_time = database.doSQL("select data from data where type = 'uptime' and created_by ='" + str(os.getppid()) + "'")[0][0]
		uptime = int(time.time()) - int(start_time)
		result = "I've been awake "
		if uptime > 86400:  # seconds/day
			days = uptime / 86400
			result += str(days) +" days, "
			uptime %= 86400
		if uptime > 3600: # seconds/hour
			hours = uptime / 3600
			result += str(hours) +" hours, "
			uptime %= 3600
		if uptime > 60: 
			hours = uptime / 60
			result += str(hours) +" minutes, "
			uptime %= 60
		result += str(uptime) +" seconds. "


		return Event("privmsg", "", self.return_to_sender(args), [ result ])

