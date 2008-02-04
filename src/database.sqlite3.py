#!/usr/bin/env python

# Copyright (C) 2008 by FKtPp
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

"""database.sqlite3.py - used for database interaction with sqlite3"""
import sqlite3
import threading, thread, ConfigParser, sys
import moobot

parser=ConfigParser.ConfigParser()
parser.read(moobot.MooBot.config_files)

try:
	dbname = parser.get("database", "name")
except ConfigParser.NoSectionError:
	print "Error: Missing [database] section in config files."
	sys.exit(0)
except ConfigParser.NoOptionError:
	print "Error:  Missing vital option in configs."
	sys.exit(0)

type = "sqlite3"


def doSQL(SQL):
	""" executes the sql statement SQL and returns a list of tupples
	containing the results"""
	results = []

	try:
		c = sqlite3.connect(dbname)
		cur = c.cursor()
		cur.execute(SQL)
	
		if SQL.split()[0].lower() == "select":
			row = cur.fetchone()
			while row != None:
				results.append(row)
				row = cur.fetchone()
	except Exception, message:
                print moobot.RED + "There was an error with the database"+\
                        " when executing " + moobot.BLUE + SQL + moobot.NORMAL
                print moobot.RED + "Exception occurred: " + moobot.BLUE + \
                        str(message) + moobot.NORMAL

	c.close()

	return results
