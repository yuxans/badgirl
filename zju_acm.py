#!/usr/bin/env python

# Copyright (C) 2005 by FKtPp
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

"""
zju_acm.py - parse the following page to find out if the problem have been done

http://acm.zju.edu.cn/user_status.php?user=intx

""" 
from moobot_module import MooBotModule
import HTMLParser2
import re
handler_list=["zju_acm"]

class zju_acm(MooBotModule, HTMLParser2.HTMLParser):
	def __init__(self):
		HTMLParser2.HTMLParser.__init__(self)
		self.regex = "^acm .+"
		self.DoneList = []
		self.do = False
		self.problem = None
		self.r = re.compile("^\d{4}$")

	def handler(self, **args):
		"""
		it's just dirty
		"""
		import string
		from irclib import Event
		self.problem = args["text"].split(None, 2)[2]
		if self.r.match(self.problem):
			text = "Problem %s is at http://acm.zju.edu.cn/show_problem.php?pid=%s\n" % (self.problem, self.problem)
 			import urllib2
 			self.feed(urllib2.urlopen("http://acm.zju.edu.cn/user_status.php?user=intx").read())
			if self.problem in self.DoneList:
 				text += "Oops, The problem %s was already done." % (self.problem,)
 			else:
 				text += "Hey, problem %s wasn't done. Let's hack it~" % (self.problem,)
		else:
			text = "%s is not a valid PROBLEM ID, see http://acm.zju.edu.cn/ for details" % (self.problem,)
		text += " TOTAL RESOLVED: %d" % (len(self.DoneList))
		target = self.return_to_sender(args)
		result = Event("privmsg", "", target, [ text ])
		return result

	def handle_starttag(self, tag, attrs):
		if tag == "td" and attrs == [("width", "60%"),("align", "left"),("rowspan", "4")]:
			self.do = True
		else:
			pass


	def handle_data(self, data):
		if data == "Email:&nbsp;":
			self.do = False
		if self.do == True and self.r.match(data):
			self.DoneList.append(data)
		else:
			pass
