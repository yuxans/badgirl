#!/usr/bin/env python

# Copyright (c) 2002 Daniel DiPaolo, et. al.
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

from irclib import Event
from irclib import Event
from moobot_module import MooBotModule
handler_list = ["rot13", "reverse", "decode"]

class rot13(MooBotModule):
	def __init__(self):
		self.regex = "^rot13 .+$"

	def handler(self, **args):
		"Qbrf n fvzcyr ebg13, abguvat snapl"
		import string
	
		msg = " ".join(args["text"].split(" ")[2:])
		newstring = msg.encode("rot_13")
		return Event("privmsg", "", self.return_to_sender(args), [newstring])

class reverse(MooBotModule):
	def __init__(self):
		self.regex = "^reverse .+"

	def handler(self, **args):
		"gnirts a sesreveR"
	
		from string import join
		orig_string = join(args["text"].split(" ")[2:])
		newstring = ""
		for i in range(1, len(orig_string)+1):
			newstring += orig_string[-i]
		return Event("privmsg", "", self.return_to_sender(args), [newstring])

class decode(MooBotModule):
	def __init__(self):
		self.regex = "^(?:decode from \S+ .+)$"

	def handler(self, **args):
		(cmd, encodings) = args['text'].split(' ', 4)[2:4]
		if cmd.lower() == 'from':
			rawmsg = args['event'].rawdata().split(' ', 6)[6]
			encodings = encodings.lower().split(":")
			msg = rawmsg
			for encoding in encodings:
				if encoding == 'base64':
					try:
						msg = msg.decode(encoding)
					except:
						msg = "decode from %s failed" % encoding
						break
				else:
					msg = msg.decode(encoding, "replace")
		else:
			msg = "not implemented"

		return Event("privmsg", "", self.return_to_sender(args), [ msg ])
