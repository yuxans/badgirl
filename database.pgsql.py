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

"""database.pgsql.py - used for database interaction with PostgreSQL"""
from pyPgSQL import PgSQL
import threading, thread, ConfigParser, sys
import moobot

parser=ConfigParser.ConfigParser()
parser.read(moobot.MooBot.config_files)

try:
	dbhostname = parser.get("database", "hostname")
	dbname = parser.get("database", "name")
	dbport = parser.getint("database", "port")
	dbuser = parser.get("database", "username")
	dbpass = parser.get("database", "password")
except ValueError:
	print "Error: Bad port number in DB config"
	sys.exit(0)
except ConfigParser.NoSectionError:
	print "Error: Missing [database] section in config files."
	sys.exit(0)
except ConfigParser.NoOptionError:
	print "Error:  Missing vital option in configs."
	sys.exit(0)


num_connections = 4 # 4 different connections for different threads to
		    # use, since two can't use the same one at the same
		    # time
botdbs = []
dblocks = []
notify = threading.Event()
notify.set()
countLock = thread.allocate_lock()

type = "pgsql"

print "initializing DB connections & locks"
for j in range(num_connections):
	botdbs.append(PgSQL.connect(host = dbhostname, user = dbuser, database = dbname, port = dbport, password=dbpass))
	dblocks.append(thread.allocate_lock())


def doSQL(SQL):
	""" executes the sql statement SQL and returns a list of tupples
	containing the results"""
	#grab a DB connection to use
	connection_num = getAConnection()
	#print moobot.RED + "got connection " + moobot.NORMAL + str(connection_num)
	results = []
	try:
		cur = botdbs[connection_num].cursor()
		cur.execute(SQL)
		if SQL.split()[0].lower() == "select":
			row = cur.fetchone()
			while row != None:
				results.append(row)
				row = cur.fetchone()
		else:
			botdbs[connection_num].commit()
        except Exception, message:
                print moobot.RED + "There was an error with the database"+\
                        " when executing " + moobot.BLUE + SQL + moobot.NORMAL
                print moobot.RED + "Exception occurred: " + moobot.BLUE + \
                        str(message) + moobot.NORMAL


	#print moobot.GREEN + "releasing connection " + moobot.NORMAL+ str(connection_num)
	# give the connection back
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
			botdbs[cnum] = PgSQL.connect(host = dbhostname, user = dbuser, database = dbname, port = dbport, password=dbpass)
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
			
