#!/usr/bin/env python

# Copyright (c) 2002 Daniel DiPaolo and Brad Stewart
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

"""handler.py - a class that wraps around the bot modules, a list of Handlers
is stored in the MooBot instance, and the list is traversed with a chain of
responsability pattern to find which handler will handle any given event.
"""

class Handler:
	"""This class defines how chat messages are processed to generate chat
	events that the bot acts out"""
	GLOBAL = "global"
	LOCAL = "local"

	def __init__(self, module, className, type=0):
		from re import compile
		self.instance = getattr(module, className)()
		self.module = module
		self.className = className
		self.regex = compile(self.instance.regex)
		self.type = type or self.instance.type

	def __str__(self):
		return '"' + self.instance.regex + '": ' + self.className
	
	def __cmp__(self, other):
		return cmp(self.instance, other.instance)

	def __eq__(self, other):
		return repr(self) == repr(other)

	def reInstantiate(self):
		from re import compile
		print "reloading %s from %s" % (self.className, self.module.__name__)
		reload(self.module)
		self.instance = getattr(self.module, self.className)()
		self.regex = compile(self.instance.regex)

	def toggle_global(self):
		if self.type == Handler.LOCAL:
			self.type = Handler.GLOBAL
		else:
			self.type = Handler.LOCAL
	def pattern(self):
		return self.regex.pattern
	def func_name(self):
		return self.className

