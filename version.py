#!/usr/bin/env python

# Copyright (c) 2002 Vincent Foley, et. al.
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


from moobot_module import MooBotModule
handler_list=["version"]

class version(MooBotModule):
	def __init__(self):
		self.regex="^version .+"

	def handler(self, **args):
		"""
		This will go on freshmeat to look for a software version
		"""
		import string, urllib2, re

		# Get the name of the software and put the name in all lowercase
		name	= string.joinfields(args["text"].split()[2:])
		name	= name.lower()
		name	= string.replace(name, " ", "+")

		# The URL
		url	 = "http://freshmeat.net/projects-xml/" + name

		# In the document, we are looking for latest_version to tell us the version
		regex	= re.compile("^\s*<latest_release_version>.*</latest_release_version>$", re.IGNORECASE)
		xml_doc	= urllib2.urlopen(url).readlines()
		version	= None

		for line in xml_doc:
			if regex.match(line):
				version = line

		if version == None:
			output	= "Can't find %s on [fm]" % name
		else:
			version = version.strip() # Remove spaces and '\n'
			version = version.replace("<latest_release_version>", "")
			version = version.replace("</latest_release_version>", "")
			output	= "Latest version of %s according to [fm]: %s" % (name, version)

		target = self.return_to_sender(args)

		from irclib import Event
		return(Event("privmsg", "", target, [output]))

