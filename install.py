#!/usr/bin/env python

# Copyright (c) 2002 Brad Stewart and Daniel DiPaolo
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

"""  install.py -- This script handles the initial configuration and setup
	for the bot.  It checks module dependencies, sets up the database,
	and other stuff. """

import sys

ESCAPE = "\33"
RED = ESCAPE + "[31m"
GREEN = ESCAPE + "[32m"
YELLOW = ESCAPE + "[33m"
BLUE = ESCAPE + "[34m"
PURPLE = ESCAPE + "[35m"
NORMAL = ESCAPE + "[0m"
UNDERLINE = ESCAPE + "[4m"
BLINK = ESCAPE + "[5m"

class module:
	""" a module, for checking dependencies """
	def __init__ (self, statement, critical, description):
		self.statement = statement
		self.critical = critical
		self.description = description


class modulesTest:
	""" Used for checking whether required modules are available. """
	def __init__(self):
		self.modules = {}
		self.missingModules = []
		self.add_module( "irclib", module("import irclib", 1, \
		"This should never fail.  If it does, it means the set up script " + \
		"was executed somewhere other than in a complete moobot source " + \
		"tree."))
		self.add_module("ircbot", module("import ircbot", 1, \
		"This should never fail.  If it does, it means the set up script " + \
		"was executed somewhere other than in a complete moobot source tree."))
		self.add_module("gtk", module("import gtk", 0, \
		"This module is used by tableview.py, which is not critical to the "+ \
		"operation of moobot.  It is a small utility to easily view and "+ \
		"alter data in your moobot's tables."))
		self.add_module("GTK", module("import GTK", 0,  \
		"This module is used by tableview.py, which is not critical to "+ \
		"the operation of moobot.  It is a small utility to easily view " + \
		"and alter data in your moobot's tables."))
		self.add_module("PgSQL", module("from pyPgSQL import PgSQL", 0, \
		"This module is used for communicating with a PostgreSQL database.  "+\
		"Though it is not necessary, if you do not have a Postgres or MySQL "+\
		"database running, you won't be able to use a large number of the "+\
		"bot's modules."))
		self.add_module("MySQLdb", module("import MySQLdb", 0, \
		"This module is used for communicating with a MySQL database.  "+\
		"Though it is not necessary, if you do not have a Postgres or " + \
		"MySQL database running, you won't be able to use a large number " + \
		"of the bot's modules."))
	
	def add_module(self, module_name, module):
		self.modules[module_name] = module
	
	def run_test(self):
		print "Checking modules..."
		for lib in self.modules.keys():
			print "Checking for " + lib + "...",
			try:
				exec(self.modules[lib].statement)
				print GREEN + "OK" + NORMAL
			except:
				self.missingModules.append(lib)
				print RED + "MISSING" + NORMAL
		print "done"
		return len(self.missingModules)
	
	def print_missing_modules(self):
		for lib in self.missingModules:
			print RED + lib + NORMAL + "\t\t" + \
				self.modules[lib].description
			print
			
	def missing_criticals(self):
		result = 0
		for lib in self.missingModules:
			if (self.modules[lib].critical == 1):
				result = 1
		return result

	def db_names(self):
		""" returns a list containing the names of all found
			database libraries"""
		result = []
		if "PgSQL" not in self.missingModules:
			result.append("PgSQL")
		if "MySQLdb" not in self.missingModules:
			result.append("MySQLdb")
		return result

def basicConfig(configFile):
	""" Create the general configuration for the bot. """
	import string
	print "\n\nNow we'll do some general configuration of the bot.  The "+\
		"result will be written to moobot.conf.  These values " + \
		"don't have to be final -- you can change them later.\n"

	nick = ""
	server = ""
	port = 0
	channels = ""
	shorthand = ""
	while nick == "":
		nick = raw_input("Enter bot's nick: ")
	while server == "":
		server = raw_input("Enter the server to use: ")
	while port == 0:
		try:
			port = string.atoi(raw_input("What port on the server? "))
		except:
			pass

	while channels == "":
		channels = raw_input("Enter channel list, separated by spaces: ")
	while shorthand == "":
		shorthand = raw_input("Enter the shorthand address character for\n" \
		+ "the bot (the shorthand address character is used to address\n" \
		+ "the bot when you don't want to type the bots whole name, like\n" \
		+ "'~praise foo' instead of	'moobot: praise foo' has '~' as the\n" \
		+ "shorthand address character): ")
	configFile.write("[connection]\n")
	configFile.write("nick = " + nick + "\n")
	configFile.write("server = " + server + "\n")
	configFile.write("port = " + `port` + "\n")
	configFile.write("channels = " + channels + "\n")
	configFile.write("\n[extras]\n")
	configFile.write("shorthand = " + shorthand + "\n")
	

def getDbName(options):
	import string
	if len(options) == 0:
		raise IndexError("Empty Array.")
	print "The following database libraries were found on your system:"
	for index in range(len(options)):
		print index, "\t", options[index]
	print "Which do you want to use?"
	choice = -1
	while choice < 0 or choice >= len(options):
		try:
			choice = string.atoi(raw_input())
		except:
			pass
	return options[choice]

def setUpDB(configFile, database):
	""" Sets the bot up to use postgres or MySQL"""
	import sys, os, getpass, string

	print """In order to support multiple DBMS, we use multiple database
modules with a common interface, and create a symlink to
from "database.py" to the one we want to use.  I will now
create a symlink from database.py to """,
	if database == "PgSQL":
		print "database.pgsql.py.",
	if database == "MySQLdb":
		print "database.mysql.py.",

	print	""" If you are running an OS that does not support symlinks,
you will have to manually copy the apropriate module to
database.py.
(press enter to continue)"""
	raw_input()
	try:
		if database == "PgSQL":
			os.symlink("database.pgsql.py", "database.py")
		if database == "MySQLdb":
			os.symlink("database.mysql.py", "database.py")
	except:
		print "There was an error creating the symlink.  Continue?"
		cont = raw_input()
		if cont.lower() != "y" and cont.lower() != "yes":
			sys.exit(1)
	
	print """We'll now need connection info so the bot can connect
to the database.  You will be asked for, among other things,
a username and database name for the bot to use.  If you
haven't created a database or user yet, don't worry, we'll
do that later. """

	username, password, port, host, dbname = makeDbConfig(database, configFile)

	if database == "PgSQL":
		print "Do you want to create the database user now?"
		createdbuser = raw_input()
		if createdbuser.lower() == "y" or createdbuser.lower() == "yes":
			makePgUser(username, password, port, host)
		print "Do you want to create the database now?"
		createdb = raw_input()
		if createdb.lower() == "y" or createdb.lower() == "yes":
			makePgDB(username, password, port, host, dbname)

	elif database == "MySQLdb":
		print "Do you want to create the database now?"
		createdb = raw_input()
		if createdb.lower() == "y" or createdb.lower() == "yes":
			suser = raw_input("Enter the MySQL superuser name: ")
			supass = getpass.getpass("Enter the MySQL superuser's password:")
			makeMyDB(username, password, host, dbname, suser, supass)
		print "Do you want to create the database user now?"
		createdbuser = raw_input()
		if createdbuser.lower() == "y" or createdbuser.lower() == "yes":
			if suser == "":
				suser = raw_input("Enter the MySQL superuser name: ")
			if supass == "":
				supass = getpass.getpass("Enter the MySQL superuser's password:")
			makeMyUser(username, password, host, dbname, suser, supass)


def makeMyDB(username, password, host, dbname, suser, supass):
	import sys, os, getpass, string
	# Create the database on the host specified with the superuser
	if os.system("mysqladmin -h " + host + " -u " + suser + " --password=" + supass + " create " + dbname ):
		print "Database creation failed."
		raw_input("(press enter to continue)")

def makeMyUser(username, password, host, dbname, suser, supass):
	import sys, os, getpass, string, socket

	# Get the current hostname so we can get access on the remote db
	hostname = socket.gethostname()
	
	# Create the command that will grant the 'normal' user (what the
	# bot will access the database as) all privileges on the database
	# FIXME: Do we really want them to have all privileges?
	command ="grant all privileges on " + dbname + ".* to " + username + \
	"@" + hostname + " identified by '" + password + "'"
	#print command

	# Actually execute the command above
	os.system('mysql -h ' + host + ' -u ' + suser + ' --password=' + supass + \
	' -e "' + command + '" ')

	print "reloading MySQL Grant tables... ",
	if os.system("mysqladmin -h " + host + " -u " + suser + " --password=" + supass + " reload" ):
		print RED + "FAILED!"
	else:
		print "done."

	print "I will now create the table structure for the database."
	raw_input("(press enter to continue)")

	os.system("mysql -h " + host + " -u " + username + " --password=" + password + " " + dbname + " < table-skel.mysql.sql")
	os.system("mysql -h " + host + " -u " + username + " --password=" + password + " " + dbname + " < data.sql")
	print "done."

def makeDbConfig(database, configFile):
	import sys, os, getpass, string
	username = ""
	host = ""
	port = 0
	password = ""
	vpassword = ""
	dbname = ""
	configFile.write("\n\n[database]\n")

	while username == "":
		username = raw_input("Enter bot's database user name: ")

	configFile.write("username = " + username + "\n")
	while host == "":
		host = raw_input("Enter the name of the host running the DB: ")
	configFile.write("hostname = " + host + "\n")
	if database == "PgSQL":
		while port == 0:
			try:
				port = string.atoi(raw_input("Enter the port of the dbms: "))
			except:
				pass
		configFile.write("port = " + `port` + "\n")

	while dbname == "":
		dbname = raw_input("Enter the name of the database: ")
	configFile.write("name = " + dbname + "\n")

	while password == "" or password !=  vpassword:
		password = getpass.getpass("Enter the bot's password: ")
		vpassword = getpass.getpass("re-enter the bot's password: ")
		if password != vpassword:
			print "Passwords do not match."
	configFile.write("password = " + password + "\n")
	return [username, password, port, host, dbname]



def makePgDB(username, password, port, host, dbname):
	os.system("echo " + password + " | createdb -h " + host + \
		" -p " + `port` + " -U" + username + " " + dbname)
	raw_input("(press enter to continue)")
	print "I will now create the table structure for the database."
	raw_input("(press enter to continue)")
	os.system("echo " + password + " | psql -h " + host + " -d " + dbname + " -f " + \
	"table-skel.pgsql.sql -U "  + username)
	os.system("echo " + password + " | psql -h " + host + " -d " + dbname + " -f " + \
	"data.sql -U "  + username)
	print("done.")

	
def makePgUser(username, password, port, host):
		supass = getpass.getpass("Enter the postgres superuser's password:")
		raw_input("(press enter to continue)")
		os.system("echo -e \"" + password + "\n" +password + "\n" + \
		supass + "\"| " +  "createuser -h " + host + \
		" -p " + `port` + " -d -A -P " +  username)
		raw_input("(press enter to continue)")

def setUpBotOwner(database):
	import getpass, os

	if database == "":
		return

	print "Input a nickmask for yourself on IRC that will be" 
	print "granted all_priv (leave it blank to skip this step)"
	nickmask = raw_input("Nickmask (e.g. foo!bar@*.myisp.com): ")
	
	# Process nickmask
	nickmask.replace("*", "%")
	nickmask.replace("\"", "\\\"")
	nickmask.replace("'", "\\'")
	nickmask.replace("\\", "\\\\")

	# Get username, pass, all that good stuff for the DB
	username = raw_input("DB User for bot: ")
	password = getpass.getpass("DB Password for bot: ")
	hostname = raw_input("Hostname of machine DB is on: ")

	if database == "MySQLdb":
		# Build command to grant all_priv
		command = "insert into grants(hostmask, priv_type) values('" + \
			nickmask + "', 'all_priv')"

		# Execute command
		os.system('mysql -h ' + hostname + ' -u ' + username + \
			' --password=' + password + ' -e "' + command + '" ')
		
	elif database == "PgSQL":
		# Build command to grant all_priv
		command = "insert into grants(hostmask, priv_type) values('" + \
			nickmask + "', 'all_priv')"
		# Execute command
		os.system('psql -h ' + hostname + ' -U ' + username + \
			' --password ' + password + '-c "' + command + '"')
	else:
		print "unknown database type: '" + database + "'"
	

def main():
	print "We're going to start by checking whether you have all " +\
		"required modules."
	raw_input("(press enter to continue)")
	moduleCheck = modulesTest()

	#check if all the modules we need are present.
	if (moduleCheck.run_test() == 0 ):
		print "All modules found."
	else:
		# List the missing modules, and explain them
		print "The following modules were found to be missing:\n"
		moduleCheck.print_missing_modules()

		#if any missing modules are mandatory, say so and die.
		if (moduleCheck.missing_criticals()):
			print RED + "Some of these modules are critical.  " + \
			"Please Correct the problems listed above."
			sys.exit(1)

		#if no database modules were found, warn the user and ask
		# whether they want to continue
		elif len(moduleCheck.db_names()) == 0:
			print RED + "No database libraries were found (for " +\
				"either MySQL or PostgreSQL.  While a data"+\
				"base is not entirely necessary, you will "+\
				"not be able to use a large portion of the" +\
				" bot's functionality without one, and will"+\
				" have to edit moobot.py to remove those "+\
				"modules that requre database support.  For"+\
				" this reason, this configure script will "+\
				"not continue.  If you do want to continue,"+\
				"without database support, "+\
				" you will have to edit this script to allow"+\
				" the configuration to proceed beyond this " +\
				"point.  Otherwise, please install the "+\
				"appropriate library for the DBMS you want"+\
				" to use."
			sys.exit(1)
		else:
			print "No mandatory modules were missing.  If any " +\
				"tests above returned \"MISSING\", read "+\
				"the printed messages."
			raw_input("(press enter to continue)")

	configFile = open("moobot.conf", "w")
	basicConfig(configFile)

	database =  getDbName(moduleCheck.db_names())
	print database
	setUpDB(configFile, database)

	# Give the owner of the bot 'all_priv'
	setUpBotOwner(database)

	configFile.close()
	print "Configure is all done.  Your bot should be functional"
	print "now.  Fire 'er up with \"python moobot.py\" and see what"
	print "happens.  :)"
	

if __name__ == '__main__':
	main()
