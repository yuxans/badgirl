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

"""priv.py - used for checking privelages on certain functions from a database """

from moobot_module import MooBotModule
handler_list = ["grantPriv", "revokePriv", "showPriv"]

def checkPriv(hostmask, privilege):
	"""checks if the user identified by hostmask has privilege privilege
	returns 0 if the nick/hostmask doesn't have that privilege
	returns 1 if they do"""
	import database
	value=database.doSQL("select count(hostmask) from grants where '" + hostmask + "' LIKE hostmask and (priv_type = '" + privilege + "'  or priv_type = 'all_priv')")
	return value[0][0]

class grantPriv(MooBotModule):
	def __init__(self):
		self.regex="^grant \w+ to .+"

	def handler(self, **args):
		""" gives a nick/host mask a privileve """
		from irclib import Event
		from irclib import nm_to_n
		import database
		import string
		target=args["channel"]
		if args["type"] == "privmsg":
			target=nm_to_n(args["source"])
		privilege = args["text"].split()[2]
	
		mask = args["text"].split()[4]
	
		if checkPriv(args["source"], "grant_priv") == 0 or checkPriv(args["source"], privilege) == 0:
			return Event("privmsg", "", target, [ "You don't have permission to do that." ])
	
		mask = string.replace(mask, "*", "%")
		if checkPriv(mask , privilege) != 0:
			return Event("privmsg", "", target, [ mask + " already has " + privilege +"." ])

		database.doSQL("insert into grants(hostmask, priv_type) values('" + mask + "', '" + privilege  + "')")
		return Event("privmsg", "", target, [ "Granted " + privilege + " to " + mask + "." ])
	
class revokePriv(MooBotModule):
	def __init__(self):
		self.regex="^revoke \w+ from .+"

	def handler(self, **args):
		""" revokes a privilege from a  nick/host """
		from irclib import Event
		from irclib import nm_to_n
		import database
		import string
		target=args["channel"]
		if args["type"] == "privmsg":
			target=nm_to_n(args["source"])
	
		privilege = args["text"].split()[2]
		mask = args["text"].split()[4]
	
		if checkPriv(args["source"], "grant_priv") == 0 or checkPriv(args["source"], privilege) == 0:
			return Event("privmsg", "", target, [ "You don't have permission to do that." ])
	
		mask = string.replace(mask, "*", "%")
	
		if checkPriv(mask , privilege) == 0:
			return Event("privmsg", "", target, [ mask + " does not have " + privilege +"." ])
	
		database.doSQL("delete from grants where hostmask = '" + mask + "' and priv_type = '" + privilege +"'")
		return Event("privmsg", "", target, [ "Revoked " + privilege + " from " + mask + "." ])
		
class showPriv(MooBotModule):
	def __init__(self):
		self.regex="^privs( .+)?$"

	def handler(self, **args):
		"""Checks what privs a given nick has."""
		from irclib import Event
		import database, re

		text = ""
		hostmask = args["source"]
		for result in database.doSQL("select priv_type from grants where '" + hostmask + "' LIKE hostmask"):
			text += result[0] + ", "
		text = re.sub(", $", "", text)
		return Event("privmsg", "", self.return_to_sender(args), [ "Your privs are : " + text ])
		
