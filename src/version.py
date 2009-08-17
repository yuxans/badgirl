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
import re
handler_list=["version"]

class version(MooBotModule):
	def __init__(self):
		self.regex="^version .+"
		self.rTitle = re.compile(".*?<title>.*?</title>.*?<title>(.*?)</title>", re.I | re.S)

	def handler(self, **args):
		"""
		This will go on freshmeat to look for a software version
		"""
		import httpfetcher

		# Get the name of the software and put the name in all lowercase
		name = self.getText(args, 1).lower().replace(" ", "+")

		url = "http://freshmeat.net/projects/%s/releases.atom" % name
		error = None
		match = None
		try:
			fetcher = httpfetcher.urlopen(url, httpfetcher.RegexChecker(self.rTitle))
			match = fetcher.fetch()
		except socket.timeout:
			error = "timeout"

		if error:
			output	= "failed to check version for %s: %s" % (name, error)
		else:
			if not match:
				output	= "Can't find %s on [fm]" % name
			else:
				version = match.group(1)
				output	= "Latest version of %s according to [fm]: %s" % (name, version)

		return self.msg_sender(args, output)
