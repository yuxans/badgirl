#!/usr/bin/env python

# Copyright (c) 2002 Brad Stewart
# Portions taken from Joe Wreschnig's DateTime.pm for Funbot.
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
handler_list=["cputime", "uptime", "date", "ddate", "xday"]

class cputime(MooBotModule):
	def __init__(self):
		self.regex = "^cputime$"

	def handler(self, **args):
		"""Reports CPU time usage for the current thread."""
		from os import times
		from irclib import Event
		target=args["channel"]
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
		return Event("privmsg", "", target,
			     ["User time: " + str(times()[0]) + " seconds, " + \
			      "system time: " + str(times()[1]) + " seconds.  "+\
			      "Childrens' user time: " + str(times()[2]) + ", "+\
			      "childrens' system time: " + str(times()[3])])

class uptime(MooBotModule):
	def __init__(self):
		import os, database, time
		self.regex = "^uptime$"
		self.pid = os.getpid()

		database.doSQL("DELETE FROM data WHERE type = 'uptime' AND " + \
			       "created_by != '" + str(self.pid) + "'");
		if len(database.doSQL("SELECT * FROM data WHERE " + \
				      "type = 'uptime' AND " + \
				      "created_by ='" + str(self.pid) + "'")) == 0:
			database.doSQL("INSERT INTO data (data, type, created_by) "+\
				       "VALUES('" + str(int(time.time())) + "', "+\
				       "'uptime', '" + str(self.pid) + "')")

	def handler(self, **args):
		import database
		from irclib import Event
		from seen import time2str
		start_time = database.doSQL("SELECT data FROM data WHERE " + \
					    "type = 'uptime' and " + \
					    "created_by ='" + str(self.pid) + \
					    "'")[0][0]
		result = "I've been awake for " + time2str(int(start_time))

		return Event("privmsg", "", self.return_to_sender(args), [ result ])

class date(MooBotModule):
	def __init__(self):
		self.regex = "^date( (utc|rfc|iso))?$"

	def handler(self, **args):
		import os
		from irclib import Event

		input = args["text"].split()
		try:
			arg = input[2]
			if (arg == "utc"):
				cline = " --universal"
			elif (arg == "rfc"):
				cline = " --rfc-822"
			elif (arg == "iso"):
				cline = " --iso-8601=seconds"
		except IndexError:
			cline = ""

		dateprog = os.popen("/bin/date" + cline)
		datestr = dateprog.read()
		return Event("privmsg", "", self.return_to_sender(args), \
			     [ datestr ])

class ddate(MooBotModule):
	def __init__(self):
		self.regex = "^ddate$"

	def handler(self, **args):
		import os
		from irclib import Event

		if os.path.exists("/usr/bin/ddate"):
			ddate = os.popen("/usr/bin/ddate '+Today is %{%A, the %e day of %B%}, YOLD %Y. %NCelebrate %H.'")
			message = ddate.read()
		else:
			message = "This aneristic computer doesn't have ddate installed..."

		return Event("privmsg", "", self.return_to_sender(args), \
			     [ message ])
	

class xday(MooBotModule):
	def __init__(self):
		self.regex = "^xday$"

	def handler(self, **args):
		import os
		from irclib import Event

		if os.path.exists("/usr/bin/ddate"):
			ddate = os.popen("/usr/bin/ddate '+%X days until X-Day. %.'")
			message = ddate.read()
		else:
			message = "This pink computer doesn't have ddate installed..."

		return Event("privmsg", "", self.return_to_sender(args), \
			     [ message ])
