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
handler_list = ["grantPriv", "revokePriv", "listPriv", "showPriv", "reloadPriv"]

privCache = None

def flushPriv():
	global privCache
	privCache = None

def checkPriv(hostmask, privilege):
	"""checks if the user identified by hostmask has privilege privilege
	returns 0 if the nick/hostmask doesn't have that privilege
	returns 1 if they do"""
	return getPriv(hostmask, privilege) and 1 or 0

def getPriv(hostmask, privilege):
	global privCache

	if not privCache:
		privCache = {}
		import database, re
		privs = database.doSQL("SELECT priv_type,hostmask FROM grants ORDER BY priv_type")
		for priv in privs:
			ptype, pmask = priv
			regex = re.compile(re.escape(pmask).replace("\\%", ".*"), re.I)
			if not privCache.has_key(ptype):
				privCache[ptype] = []
			privCache[ptype].append(regex)

	if privCache.has_key(privilege):
		for regex in privCache[privilege]:
			if regex.match(hostmask):
				return hostmask

	if privilege != 'all_priv' and privCache.has_key('all_priv'):
		for regex in privCache['all_priv']:
			if regex.match(hostmask):
				return hostmask
	return False

class grantPriv(MooBotModule):
	def __init__(self):
		self.regex="^grant \w+ to .+"

	def handler(self, **args):
		""" gives a nick/host mask a privileve """
		from irclib import Event
		from irclib import nm_to_n
		import database

		target=args["channel"]
		if args["type"] == "privmsg":
			target=nm_to_n(args["source"])
		privilege = args["text"].split()[2]
	
		mask = args["text"].split()[4]
	
		if checkPriv(args["source"], "grant_priv") == 0 or checkPriv(args["source"], privilege) == 0:
			return Event("privmsg", "", target, [ "You don't have permission to do that." ])
	
		mask = mask.replace("*", "%")
		if checkPriv(mask , privilege) != 0:
			return Event("privmsg", "", target, [ mask + " already has " + privilege +"." ])

		database.doSQL("insert into grants(hostmask, priv_type) values('" + self.sqlEscape(mask) + "', '" + self.sqlEscape(privilege)  + "')")
		flushPriv()
		return Event("privmsg", "", target, [ "Granted " + privilege + " to " + mask ])
	
class revokePriv(MooBotModule):
	def __init__(self):
		self.regex="^revoke \w+ from .+"

	def handler(self, **args):
		""" revokes a privilege from a  nick/host """
		from irclib import Event
		from irclib import nm_to_n
		import database

		target=args["channel"]
		if args["type"] == "privmsg":
			target=nm_to_n(args["source"])
	
		privilege = args["text"].split()[2]
		mask = args["text"].split()[4]
	
		if checkPriv(args["source"], "grant_priv") == 0 or checkPriv(args["source"], privilege) == 0:
			return Event("privmsg", "", target, [ "You don't have permission to do that." ])
	
		mask = mask.replace("*", "%")
	
		if checkPriv(mask , privilege) == 0:
			return Event("privmsg", "", target, [ mask + " does not have " + privilege +"." ])
	
		database.doSQL("delete from grants where hostmask = '" + self.sqlEscape(mask) + "' and priv_type = '" + self.sqlEscape(privilege) +"'")
		flushPriv()
		return Event("privmsg", "", target, [ "Revoked " + privilege + " from " + mask + "." ])
		
class listPriv(MooBotModule):
	def __init__(self):
		self.regex="^listpriv$"

	def handler(self, **args):
		""" gives a nick/host mask a privileve """
		from irclib import Event, IrcStringIO
		import database
	
		if checkPriv(args["source"], "list_priv") == 0:
			return Event("privmsg", "", self.return_to_sender(args), [ "You don't have permission to do that." ])
	
		privs = database.doSQL("SELECT priv_type,hostmask FROM grants ORDER BY priv_type,hostmask")
		buffer = IrcStringIO("Privileges List:")
		last = None
		for i in privs:
			if last == i[0]:
				buffer.write(' ' + i[1] + ' ;;')
			else:
				last = i[0]
				buffer.write(' [' + i[0] + '] ' + i[1] + ' ;;')
		return Event("privmsg", "", self.return_to_sender(args), [ buffer.getvalue() ])
	
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
		
class reloadPriv(MooBotModule):
	regex = "^reloadpriv$"

	def handler(self, **args):
		flushPriv()
		from irclib import Event
		return Event("privmsg", "", self.return_to_sender(args), [ "privilege reloaded" ])
