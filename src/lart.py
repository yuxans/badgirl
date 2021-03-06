#!/usr/bin/env python

# Copyright (c) 2002 Brad Stewart and Daniel DiPaolo
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

"""lart.py - moobot Luser Attitue Readjustment Tool functions

lart, punish, praise
"""
from moobot_module import MooBotModule
handler_list = ["lart", "praise", "add"]

class lart(MooBotModule):
	def __init__(self):
		self.regex = "^(lart|punish) .*"

	def handler(self, **args):
		"""punishes a thing"""
		from irclib import nm_to_n
		import re
		# Replace occurrences of "me" with the person's name
		name_w_spaces = " " + nm_to_n(args["source"]) + " "
		text = re.sub("(\sme\s|\sme$|^me\s)", name_w_spaces, args["text"])
		# Replace trailing or leading spaces (we may introduce them with
		# the previous line)
		text = re.sub("(^\s+|\s+$)", "", text)

		line = makeline("lart", text)
		from irclib import Event
		return  Event("action", "", self.return_to_sender(args), [ line ])

class praise(MooBotModule):
	def __init__(self):
		self.regex = "^praise .*"

	def handler(self, **args):
		"""compliments/rewards a thing"""
		from irclib import nm_to_n
		import re
		# Replace occurrences of "me" with the person's name
		name_w_spaces = " " + nm_to_n(args["source"]) + " "
		text = re.sub("(\sme\s|\sme$|^me\s)", name_w_spaces, args["text"])
		# Replace trailing or leading spaces (we may introduce them with
		# the previous line)
		text = re.sub("(^\s+|\s+$)", "", text)

		line = makeline("praise", text)
		from irclib import Event
		return  Event("action", "", self.return_to_sender(args), [ line ])

class add(MooBotModule):
	def __init__(self):
		self.regex = "^add (8ball|lart|praise|dunno) .*"

	def handler (self, **args):
		"""adds larts and praises"""
		import priv

		from irclib import Event
		import database
		type = args["text"].split()[2]
		value = " ".join(args["text"].split()[3:])
		self.debug(value)
		if args["type"] == "privmsg":
			from irclib import nm_to_n
			target=nm_to_n(args["source"])
		else:
			target = args["channel"]
		if priv.checkPriv(args["source"], "add_lart_priv") == 0:
			return Event("privmsg", "", target, [ "You do not have permission to do that.  " ])
	
        	value = value.replace ("\\", "\\\\")
        	value = value.replace ("\"", "\\\"")
        	value = value.replace ("'", "\\'")
		database.doSQL("insert into data values('" + value + "', '" + type + "', '" + args["source"] + "')")
		return Event("privmsg", "", target, [ "Adding: \"" + value + "\" as " + type + "." ])
	
def makeline(type, target):
	"""Larts.  usage:  Moobot:  lart <user>"""
	import database, re
	target = re.sub("^[^ ]* *(lart|praise|punish)\s+", "", target)
	targets = target.split(" for ")

	if database.type == "mysql":
		line = database.doSQL("select data from data where type='" + type + "' order by rand() limit 1")[0][0]
	elif database.type=="pgsql":
		line = database.doSQL("select data from data where type='" + type + "' order by random() limit 1")[0][0]
	elif database.type == "sqlite3":
		line = database.doSQL("select data from data "\
					      "where type='%s' "\
					      "order by random(*) "\
					      "limit 1" % type)[0][0]
	line = line.replace("WHO", targets[0])
	for reason in range(1, len(targets)):
		line = line + " for " + targets[reason]
	return line

