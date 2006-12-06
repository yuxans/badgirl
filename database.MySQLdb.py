#!/usr/bin/env pythkn

# Copyright (c) 2002 Brad Stewart, et. al. 
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

"""database.mysql.py - used for database interaction with PostgreSQL"""
import MySQLdb
import Pool
import ConfigParser, sys
import moobot
from moobot import DebugErr

parser=ConfigParser.ConfigParser()
parser.read(moobot.MooBot.config_files)

try:
	dbport = int(parser.get("database", "port")) or 3306
	dbencoding = parser.get("database", "encoding")
	dbhostname = parser.get("database", "hostname")
	dbname = parser.get("database", "name")
	dbuser = parser.get("database", "username")
	dbpass = parser.get("database", "password")
except ValueError, e:
	print "Error: Bad port number in DB config or:"
	print e
	sys.exit(0)
except ConfigParser.NoSectionError:
	print "Error: Missing [database] section in config files."
	sys.exit(0)
except ConfigParser.NoOptionError:
	print "Error:  Missing vital option in configs."
	sys.exit(0)


type = "mysql"


ctor = Pool.Constructor(MySQLdb.connect,
						host = dbhostname,
						port = dbport,
						user = dbuser,
						db = dbname,
						passwd=dbpass,
						read_default_file = "~/.my.cnf",
						read_default_group = "client",
						use_unicode = True,
						charset = dbencoding)

dbConPool = Pool.Pool(ctor)

def doSQL(SQL):
	""" executes the sql statement SQL and returns a list of tuples
	containing the results"""

	results = []
#	SQL = SQL.encode(dbencoding, "backslashreplace")
#	DebugErr("executing " + SQL)

	try:
		dbconn = dbConPool.get()
		# See "pydoc MySQLdb.connection" /ping(/ for details
		dbconn.ping()
		cur = dbconn.cursor()
		cur.execute(SQL)

		results = cur.fetchall() or []
		cur.close()
		dbconn.commit()
		dbConPool.put(dbconn)
	except Exception, message:
		DebugErr(moobot.RED + "There was an error with the database"+\
			" when executing " + moobot.BLUE + SQL + moobot.NORMAL)
		DebugErr(moobot.RED + "Exception occurred: " + moobot.BLUE + \
			str(message) + moobot.NORMAL)
		raise

	return results

