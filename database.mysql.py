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
import _mysql_exceptions
import threading, thread, ConfigParser, sys
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


num_connections = 1 # 4 different connections for different threads to
		    # use, since two can't use the same one at the same
		    # time
botdbs = []
dblocks = []
notify = threading.Event()
notify.set()
countLock = thread.allocate_lock()

type = "mysql"

def newconnection():
	return MySQLdb.connect(host = dbhostname, port = dbport, user = dbuser, db = dbname, passwd=dbpass,
		read_default_file = "~/.my.cnf", read_default_group = "client",
		use_unicode = True)

print "initializing DB connections & locks"
for j in range(num_connections):
	conn = newconnection()
	botdbs.append(conn)
	dblocks.append(thread.allocate_lock())
del conn

def doSQL(SQL):
	""" executes the sql statement SQL and returns a list of tuples
	containing the results"""
	#grab a DB connection to use
	connection_num = getAConnection()
	#print moobot.RED + "got connection " + moobot.NORMAL + str(connection_num)
	results = []
	SQL = SQL.encode(dbencoding, "backslashreplace")
	DebugErr("executing " + SQL)
	try:
		cur = botdbs[connection_num].cursor()
		cur.execute(SQL)
# 		try:
# 			cur.execute(SQL)
# 		except Exception, message:
# 			DebugErr(moobot.RED + "Exception occurred: " + moobot.BLUE + \
# 				str(message) + moobot.NORMAL)
# 			DebugErr("reconnecting")
# 			conn = newconnection()
# 			botdbs[connection_num] = conn
# 			cur = conn.cursor()
# 			cur.execute(SQL)
		results = cur.fetchall() or []
	except Exception, message:
		DebugErr(moobot.RED + "There was an error with the database"+\
			" when executing " + moobot.BLUE + SQL + moobot.NORMAL)
		DebugErr(moobot.RED + "Exception occurred: " + moobot.BLUE + \
			str(message) + moobot.NORMAL)

	releaseConnection(connection_num)
	return results

def getAConnection():
	cnum = -1
	# check to see if any existing connections are free.  If not,
	# create a new one.
	while cnum == -1:
		for idx in range(len(dblocks)):
			if not dblocks[idx].locked():
				if dblocks[idx].acquire(0):
					cnum = idx
					#if checkFreeConnections() != 0:
					#	notify.set()
					break
		if cnum == -1:
			dblocks.append(thread.allocate_lock())
			botdbs.append('')
		elif cnum >= num_connections:
			print "Not enough connections, spawning a new one."
			conn = newconnection()
			botdbs[cnum] = conn
			printFreeConnections()

	return cnum

def releaseConnection(cnum):
	if cnum >= num_connections:
		botdbs[cnum].close()
		botdbs[cnum] = None
	dblocks[cnum].release()
	#notify.set()

def checkFreeConnections():
	count = 0
	string = ""
	countLock.acquire()
	for lock in dblocks:
		if not lock.locked():
			count += 1
		else:
			string += str(lock) + " is locked "
	countLock.release()
	print count , "locks are free"
	print string
	return count

def printFreeConnections(): # for debugging
	string = ""
	for idx in range(len(botdbs)):
		if dblocks[idx].locked():
			string += str(idx) + " is locked. "
		else:
			string += str(idx) + " is not locked. "
	print string
			
