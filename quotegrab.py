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

"""hi.py - dummy function that says Hi """

handler_list=["quotegrab"]

from moobot_module import MooBotModule


class quotegrab(MooBotModule):
	""" grabs a user's last quote from the 'seen' table and uses it as
	their quote for the channel in webstats."""
	def __init__(self):
		self.regex="^quotegrab\s.+$"

	def handler(self, **args):
		import database, priv, string
		from irclib import nm_to_n, Event
		user = args["text"].split()[2] # get name
		if priv.checkPriv(args["source"], "quote_priv") == 0: #check if requester is allowed to do this
			return Event("privmsg", "", self.return_to_sender(args), [ "That requires quote_priv" ])
		results = database.doSQL("select message, time from seen where nick = '%s'" % (user))
		# check if they have a "seen" entry, act accordingly
		if len(results) > 0:
			quote, time = results[0]
		else:
			return Event("privmsg", "", self.return_to_sender(args), [ "No quote available for %s" % (user) ])
		#update their webstats entry with the new info
		database.doSQL("update webstats set quote = '%s', quote_time = %s where nick = '%s' and channel = '%s'" % (string.replace(string.replace(quote, "\\", "\\\\"), "'", "\\'"), str(time), user, args["channel"]))
			
		return Event("privmsg", "", self.return_to_sender(args), [ "Grabbing quote for %s" % (user) ])
