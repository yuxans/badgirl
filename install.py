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
from os import environ

from utilities import *
ConfigFileString = ""
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
	
	def add_module(self, module_name, module):
		self.modules[module_name] = module
	
	def run_test(self):
		print "Checking modules..."
		for lib in self.modules.keys():
			print "Checking for %s ..." % lib
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
			print RED + lib + NORMAL + "\t\t" + self.modules[lib].description
			print
			
	def missing_criticals(self):
		result = 0
		for lib in self.missingModules:
			if (self.modules[lib].critical == 1):
				result = 1
		return result


def basicConfig():
	""" Create the general configuration for the bot. """

	print "\n\nNow we'll do some general configuration of the bot.  The "\
		"result will be written to moobot.conf. \n"\
		" Default values are in [ ].  These values don't have to be final "\
		"-- you can change them later.\n"
        global ConfigFileString
	nick = ""
	server = ""
	port = 0
	channels = ""
	shorthand = ""
	
	while nick == "":
		nick = raw_input("Enter bot's nick: [ircbot] " ) or "ircbot"
	while server == "":
		server = raw_input("Enter the server to use: [irc.oftc.net] ") or "irc.oftc.net"
	while port == 0:
		try:
			port = int(raw_input("What port on the server: [6669] ") or "6669")
		except:
			pass

	while channels == "":
		channels = raw_input("Enter channel list, separated by spaces: [#grasshoppers] ") or "#grasshoppers"
	while shorthand == "":
		shorthand = raw_input("Enter the shorthand address character for\n" \
		"the bot (the shorthand address character is used to address\n" \
		"the bot when you don't want to type the bots whole name, like\n" \
		"'~praise foo' instead of	'moobot: praise foo' ): [~] ") or "~"


	ConfigFileString = "[connection]\n"
	ConfigFileString += "nick = " + nick + "\n"
	""" These where added because they are needed and not written to config file """
	ConfigFileString += "realname = " + nick + "\n"
	ConfigFileString += "username = " + nick + "\n"
	ConfigFileString += "server = " + server + "\n"
	ConfigFileString += "port = " + `port` + "\n"
	ConfigFileString += "channels = " + channels + "\n"
	ConfigFileString += "\n[extras]\n"
	ConfigFileString += "shorthand = " + shorthand + "\n"

	return nick

def setUpDB(nick):
	
	import getpass
	
	print "We'll now need connection info so the bot can connect "\
		"to the database.  You will be asked for, among other things, "\
		"a username and database name for the bot to use.  If you "\
		"haven't created a database or user yet, don't worry, we'll "\
		"do that later. "

	username, password, port, host, dbname = makeDbConfig(nick)
    
	suser = raw_input("Enter the MySQL superuser name: ")
	supass = getpass.getpass("Enter the MySQL superuser's password:")
	if suser != "" and supass != "":
		createdbuser = raw_input("Do you want to create the database user now? Y/n ") or "Y"
		if createdbuser.lower() == "y" or createdbuser.lower() == "yes":
			makeMyUser(username, password, host, dbname, suser, supass)	

		createdb = raw_input("Do you want to create the database now? Y/n " ) or "Y"
		if createdb.lower() == "y" or createdb.lower() == "yes":
			makeMyDB(host, dbname, suser, supass)
	else:
		print "MySQL's superuser and/or password was not given so we skipped the database/user create questions"
	
	createdb = raw_input("Do you want to create the database tables now? Y/n " ) or "Y"
	if createdb.lower() == "y" or createdb.lower() == "yes":
		makeDbTable(host, username, password, dbname)

	return (username, password, port, host, dbname)


def makeMyDB(host, dbname, suser, supass):
	import os
	# Create the database on the host specified with the superuser
	if os.system("mysqladmin -h %s -u %s --password=%s create %s" % (host, suser, supass, dbname)):
		print "Database creation failed."
		sys.exit(1)

	raw_input("(press enter to continue)")


def makeDbTable(host, username, password, dbname):
	import os
	print "Creating table structure for the database."
	raw_input("(press enter to continue)")

	""" If either of these fails, we need to exit """
	if os.system("mysql -h %s -u %s --password=%s %s < /usr/lib/moobot/sql/table-skel.mysql.sql" % (host, username, password, dbname)):
		print RED + "FAILED!"
		sys.exit(1)

	if os.system("mysql -h %s -u %s --password=%s %s < /usr/lib/moobot/sql/data.sql" % (host, username, password, dbname)):
		print RED + "FAILED!"
		sys.exit(1)
	print "done."

def makeMyUser(username, password, host, dbname, suser, supass):
	import os, socket

	if host != "localhost":
		hostname = socket.gethostname()
	else: 
		hostname = host

	# Create the command that will grant the 'normal' user (what the
	# bot will access the database as) all privileges on the database
	# FIXME: Do we really want them to have all privileges?
	command = "GRANT ALL ON %s.* TO %s@%s IDENTIFIED BY '%s'" % (dbname, username, hostname, password)

	# Actually execute the command above
	if os.system('mysql -h %s -u %s --password=%s -e "%s"' % (hostname, suser, supass, command)) :
		print RED + "FAILED!"
		sys.exit(1)

	print "reloading MySQL Grant tables... ",
	if os.system("mysqladmin -h %s -u %s --password=%s reload" % (host, suser, supass)):
		print RED + "FAILED!"
		sys.exit(1)
	else:
		print "done."


def makeDbConfig(nick):

	import getpass
	global ConfigFileString
	
	username = ""
	host = ""
	port = 0
	password = ""
	vpassword = ""
	dbname = ""

	ConfigFileString += "\n\n[database]\n"

	while username == "":
		username = raw_input("Enter bot's database user name: [" + dbname + "]" ) or nick
	ConfigFileString += "username = %s\n" % username

	while host == "":
		host = raw_input("Enter the name of the host running the DB: [localhost] ") or "localhost"
	ConfigFileString += "hostname = %s\n" % host

	while dbname == "":
		dbname = raw_input("Enter the name of the database: [" + nick + "]") or nick
	ConfigFileString += "name = %s\n" % dbname

	while password == "" or password != vpassword:
		password = getpass.getpass("Enter the bot's password: ")
		vpassword = getpass.getpass("re-enter the bot's password: ")
		if password != vpassword:
			print "Passwords do not match."
	ConfigFileString += "password = %s\n" % password

	return (username, password, port, host, dbname)

def setUpBotOwner(host, dbname, username, password):
	import os

	hostname = host

	print "Input a nickmask for yourself on IRC that will be" 
	print "granted all_priv (leave it blank to skip this step)"
	nickmask = raw_input("Nickmask (e.g. foo!bar@*.myisp.com): ")
	if nickmask != "":
	# Process nickmask
		nickmask.replace("*", "%")
		nickmask.replace("\"", "\\\"")
		nickmask.replace("'", "\\'")
		nickmask.replace("\\", "\\\\")

		# Get username, pass, all that good stuff for the DB

		# Build command to grant all_priv
		command = "INSERT INTO grants(hostmask, priv_type) VALUES ('%s', 'all_priv')" % nickmask
		# Execute command
		if os.system('mysql -h %s -u %s  --password=%s -e "%s" %s' % (hostname, username, password, command, dbname)):
			print RED + "FAILED!"
			sys.exit(1)
	

def main():
	print "We're going to start by checking whether you have all " +\
		"required modules."
	raw_input("(press enter to continue)")
	moduleCheck = modulesTest()
	moduleCheck.add_module("irclib", \
		module("import irclib", 1, \
			"This should never fail.  If it does, it means the set up script "\
			"was executed somewhere other than in a complete moobot source "\
			"tree."))
	moduleCheck.add_module("ircbot", 
		module("import ircbot", 1, \
			"This should never fail.  If it does, it means the set up script "\
			"was executed somewhere other than in a complete moobot source "\
			"tree."))
	moduleCheck.add_module("gtk", \
		module("import gtk", 0, \
			"This module is used by tableview.py, which is not critical to "\
			"the operation of moobot.  It is a small utility to easily view "\
			"and alter data in your moobot's tables."))
	moduleCheck.add_module("GTK", \
		module("import GTK", 0,  \
			"This module is used by tableview.py, which is not critical to "\
			"the operation of moobot.  It is a small utility to easily view "\
			"and alter data in your moobot's tables."))
	moduleCheck.add_module("MySQLdb", \
		module("import MySQLdb", 0, \
			"This module is used for communicating with a MySQL database.  "\
			"Though it is not necessary, if you do not have a Postgres or "\
			"MySQL database running, you won't be able to use a large number "\
			"of the bot's modules."))

	#check if all the modules we need are present.
	if moduleCheck.run_test() == 0:
		print "All modules found."
	else:
		# List the missing modules, and explain them
		print "The following modules were found to be missing:"
		moduleCheck.print_missing_modules()

		#if any missing modules are mandatory, say so and die.
		if (moduleCheck.missing_criticals()):
			print RED + "Some of these modules are critical.  "\
			"Please Correct the problems listed above."
			sys.exit(1)
		else:
			print "No mandatory modules were missing.  If any " \
				"tests above returned \"MISSING\", read "\
				"the printed messages."
			raw_input("(press enter to continue)")

	nick = basicConfig()

        if 'MySQLdb' not in moduleCheck.missingModules:
	    (username, password, port, host, dbname) =  setUpDB(nick)
	
	    # Give the owner of the bot 'all_priv'
	    setUpBotOwner(host, dbname, username, password)
	
	# write the missing module section

        global ConfigFileString
	ConfigFileString += "\n\n[modules]\n"
	ConfigFileString += "modulefiles = quotegrab flood_protect botmath cool ditdaw dunno eightball factoids hi ignore internal karma lart module_handling nslookup poll priv qotd seen spell stack stats stocknc tell translate version weblookup wordgame webstats eventProcess moolog"
	

	print "This is your current configuration \n"
	print "--------------------------------------------------"
	print ConfigFileString
	configok = raw_input("\n Does it look correct? Y/n ") or "Y"
	if configok.lower() == "y" or configok.lower() == "yes":
		configFile = open(environ['HOME']+"/.moobot.conf", "w")
		configFile.write(ConfigFileString)
		configFile.close()
		print "Configure is all done.  Your bot should be functional"
		print "now.  Fire 'er up with \"python moobot.py\" and see what"
		print "happens.  :)"

	else:
		main()


	

if __name__ == '__main__':
	main()
