# grabs stock quotes
# -*- coding:gbk -*-

# Copyright (C) 2004, 2005, 2006, 2007 by FKtPp, moo
# Copyright (c) 2002 Brett Kelly
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

import re
import sina_finance
from irclib import Event 
from moobot_module import MooBotModule

handler_list = ["sinaFinance"]


class sinaFinance(MooBotModule):
	def __init__(self):
		self.regex="^sina .+"
		self.sf = sina_finance.SearchEngine()

	def handler(self, **args):
		target = self.return_to_sender(args, 'nick')

		o = self.sf.search(args['text'].split()[2:])

		x = ''
		for i in o:
			x = '\n'.join((x, i.__str__()))

# 		print x

		return Event("notice", "", target, [x.strip() or "Sorry we can't find that :("])
