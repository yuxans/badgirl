#!/usr/bin/env python

import ConfigParser

# Custom exception(s)
class FailedRequiredModuleCheck(Exception): pass

def print_greeting():
	print """
Welcome to the (new and improved!) moobot installation program.

Before you can get your moobot up and running, we have to perform a few checks
to make sure your system is ready to run a moobot.  Once we've established
that, we'll prompt you for some of the required configuration options.

Running this program is entirely optional, and is only provided as a
convenience to help people set their moobots up without having to figure out
all the config file options on their own, or having to figure out what Python
modules they need for it to run properly.  If you feel comfortable reading
Python tracebacks and hacking the default configuration file provided with
moobot, then by all means feel free to do so.  Otherwise, this install program
will hopefully make setting up your moobot a simple task.

To exit the install program, simply hit ^C (Control-C) at any point.  No
configuration files will be written until the very end.

"""
	raw_input("--- Press Enter to continue ---")

def prompt_for_module_checking():
	print """
STEP 1.  Check for necessary modules

The first thing we need to do is to make sure that you have the correct Python
modules installed to run moobot.

If you feel confident that you do have them installed already, you can skip
this step.  Otherwise, it is encouraged that you allow the installer to check
and display some helpful messages describing what you may need to do in order
to properly configure your system to run a moobot.

"""
	response = raw_input("Do you wish to perform the module check? [y] ")
	return response.lower() or "y"

def prompt_for_config():
	print """
STEP 2A.  Configure bot

The next step in the installation is to perform the necessary configuration to
use the bot as you wish to.

If you are comfortable with hacking at the default config file and simply
altering the options there, then you can skip this step if you choose to do
so.  It is recommended that you do not do this unless you have installed a
moobot before, however.

"""
	response = raw_input("Do you wish to perform the configuration step? [y] ")
	return response.lower() or "y"

def prompt_for_db_config():
	print """
STEP 2B.  Database configuration and/or creation

The installer has detected valid database modules, so in this step we can
assure that you have the proper setup to use a database with the bot.

If you have an existing database set up and the account(s) to that database
are set up correctly (done in the previous step), then you may skip this step.
If you choose to continue, we will provide you with a very simple "skeleton"
database to use with your bot which you can augment simply by talking to the
bot.

"""
	response = raw_input("Do you wish to have the installer configure your DB?  [y] ")
	return response.lower() or "y"

def check_module(module_names):
	import imp
	# Receives a space-separated list of modules to test importing
	module_name_list = module_names.split()
	for module in module_name_list:
		try:
			imp.find_module(module)
		except ImportError:
			return 0
	# If we get here, they all worked :)
	return 1

def check_modules():
	# module_list is actually a list of dicts of the format:
	#  [{module_names: "module1 module2 ...",
	#    description: "Some long description here",
	#    priority: "some priority"}, ...]
	module_list = get_modules()
	found_modules = [] # List of modules found
	for module_dict in module_list:
		# If priority is required, we will bomb out sooner.  Otherwise we will
		# simply print helpful and illustrative error messages.
		print_module_check_msg(module_dict)
		if prompt_check_module() != "y": continue

		module_names = module_dict["module_names"]
		passed_check = check_module(module_names)

		if not passed_check:
			if module_dict["priority"] == "required":
				print "Required modules: %s -- NOT FOUND!" % module_names
				raise FailedRequiredModuleCheck
			else:
				print "Modules: %s -- not found, continuing anyway as they "\
					"are not required." % module_names
		else:
			found_modules.append(module_names)
			print "Found modules: %s" % module_names

	return found_modules	

def get_modules():
	# The list of modules to check is in the install.conf file.  They are in
	# all the sections that begin with "module-" (simple, eh?).  So, we just
	# grab all the section names, figure out which ones begin with "module-",
	# and then grab the contents of those, pack each into a separate dict, and
	# then make them into a list and return them.
	install_conf_parser = ConfigParser.ConfigParser()
	install_conf_parser.read("install.conf")
	sections_to_get = []
	# Get the section name list
	for section in install_conf_parser.sections():
		if section.startswith("module-"):
			sections_to_get.append(section)
	module_dicts = []	
	# Go through each section, creating a dict, and appending on to the list
	# we'll pass back
	for section_name in sections_to_get:
		temp_dict = {}
		for option in install_conf_parser.options(section_name):
			temp_dict[option] = install_conf_parser.get(section_name, option)

		module_dicts.append(temp_dict)
	return module_dicts

def config_db_modules(module_list):
	# Iterate over the list, prompting for configuration of each one.
	config_dict = {}
	for module in module_list:
		print "Found database module: %s" % module
		response = raw_input("Would you like to configure this module? [y] ").lower() or 'y'
		if response == 'y':
			# "append" the new stuff on
			config_dict.update(configure_db(module))
		else:
			print "Skipping %s module." % module

	print "Done configuring all database modules available."
	return config_dict

def print_failed_module_check():
	print """
One or more required modules is not installed on this system!  Aborting
installation.
"""


def print_module_check_msg(module_dict):
	print """
Checking for the following modules: %s
Description: %s
Priority: %s
""" % (module_dict["module_names"],
       module_dict["description"],
       module_dict["priority"])

def prompt_check_module():
	check_it = raw_input("Check for the existence of this module? [y] ").lower()
	return check_it or "y"

def configure_bot():
	# Prompt for all the necessary config options, store them in a dict, and
	# return that dict so we can write it to the config file.	

	## CONNECTION options
	nick = raw_input("What IRC nickname would you like the bot to use?  [moobot] ") or "moobot"
	username = raw_input("What username would you like the bot to use?  [moobot] ") or "moobot"
	realname = raw_input("What 'real name' would you like the bot to use (doesn't affect the bot's operation in any way)? [Moo Bot] ") or "Moo Bot"
	server = raw_input("What IRC server would you like the bot to connect to?  [irc.oftc.net] ") or "irc.oftc.net"
	port = raw_input("What port does that IRC server listen on? [6667] ") or "6667"
	channels = raw_input("What channels (list separated by space, including the pound sign) would you like your moobot to join by default? [#moobot] ") or "#moobot"
	
	return {"nick": nick, "username": username, "realname": realname, "server": server, "port": port, "channels": channels}

def configure_db(dbtype):
	print "DATABASE CONFIGURATION"
	print ""
	print "Step 1 - Get configuration options"
	hostname, port, dbname, username, password = get_db_configs()
	print "Step 2 - Database setup and creation"
	skip_setup = raw_input("Would you like to skip the DB setup/creation? [n] ") or "n"
	if skip_setup.lower() == "n":
		superuser, supass = get_db_superuser_pass()
		do_creation = raw_input("Would you like to create the database and database user according to your specifications now? [y] ") or "y"
		if do_creation.lower() == "y": 
			if dbtype == "MySQLdb":
				create_mysql_db(superuser, supass, hostname, port, dbname, username, password)
			elif dbtype == "PgSQL":
				create_pgsql_db(superuser, supass, hostname, port, dbname, username, password)
			else:
				print "Sorry, the installer doesn't know how to configure this module.  Please report this bug."
	print "Database configuration complete."

	return {"hostname": hostname, "port": port, "dbname": dbname, "username": username, "password": password}

def create_mysql_db(superuser, supass, hostname, port, dbname, username, password):
	import os
	import socket
	db_creation_prog = raw_input("If you'd like to use a different database creation program (other than mysqladmin), please enter it here (NOT RECOMMENDED) [mysqladmin] ") or "mysqladmin"
	db_import_prog = raw_input("If you'd like to use a different database creation program (other than mysql), please enter it here (NOT RECOMMENDED) [mysql] ") or "mysql"
	db_skel_file = raw_input("We provide a default skeleton database for you, but if you'd like to use a different database dump, please enter the filename here (NOT RECOMMENDED TO BE CHANGED) [table-skel.sql] ") or "table-skel.sql"
	db_data_file = raw_input("We also provide a few default data items for you, however if you wish to use your own, please enter the filename here (NOTE: MUST MATCH TABLE STRUCTURE FROM PREVIOUS FILE) [moobot.sql] ") or "moobot.sql"
	print """
Now that we have all the info we need, we need to do three things:
1. Actually create the database 
2. Import the base table structure from the specified file
3. Dump the data into the tables we just made
4. Grant access to the user given by your specified user name
5. Reload the access tables

If any of these bomb out, I will tell you which and you can try to fix it by
hand later, or you can simply try running the installer again later after
taking a look at the problem.
"""
	do_it = raw_input("One last chance, type 'y' to confirm database creation [y] ") or "y"
	if do_it.lower() == "y":
		# 1. Actually create the database 
		if os.system("%(db_creation_prog)s -h %(hostname)s -P %(port)s -u %(superuser)s --password=%(supass)s create %(dbname)s" % globals()):
			print "Database creation failed."
			return
		# 2. Import the base table structure from the specified file
		if os.system("%(db_import_prog)s -h %(hostname)s -P %(port)s -u %(superuser)s --password=%(supass)s %(dbname)s < %(db_skel_file)s" % globals()):
			print "Table import failed."
			return
		# 3. Dump the data into the tables we just made
		if os.system("%(db_import_prog)s -h %(hostname)s -P %(port)s -u %(superuser)s --password=%(supass)s %(dbname)s < %(db_data_file)s" % globals()):
			print "Data import failed."
			return
		# 4. Grant access to the user given by your specified user name
		if hostname != "localhost":
			hostname = socket.gethostname()
		grant_query = "GRANT ALL ON %(dbname)s.* TO %(username)s@%(hostname)s IDENTIFIED BY '%(password)s'" % globals()
		if os.system('%(db_import_prog)s -h %(hostname)s -P %(port)s -u %(superuser) --password=$(supass)s -e "%(grant_query)s"' % globals()):
			print "User setup failed."
			return
		# 5. Reload the access tables
		if os.system("%(db_creation_prog)s -h %(hostname)s -P %(port)s -u %(superuser)s --password=%(supass)s reload" % globals()):
			print "Grant table reload failed."
			return
		
		print "Congratulations, the entire database creation was successful!"
	

def create_pgsql_db(superuser, supass, hostname, port, dbname, username, password):
	pass

def get_db_superuser_pass():
	print """
In order to use a database with your bot, we have to create a database.  Doing
so requires database superuser privileges (not to be confused with "root" or
superuser privileges for your whole system), or at the very least, privileges
of someone who is allowed to create databases and grant privileges on that
database to other users on your system.  Consult the documentation of your
database to find out how to give a user this privilege or to find out what the
default user ID of the database superuser is (as well as the default
password).

So, for now, we have to get the superuser's username and password from you so
that we can create the database for you.  This will not be stored in any
configuration file, and is needed only for the initial setup of the database.
"""
	superuser = raw_input("Database superuser username? [root] ") or "root"
	supass = raw_input("Database superuser password? [] ") or ""
	return (superuser, supass)

def get_db_configs():
	print """
To set up the database for use with the bot, we need some rather elementary
information about configuration options you would like first.  Namely, the
IP address or hostname of the database server you wish to use, what port it
listens on, and what username and password you wish to use to access the
database.  The database need not be created yet, as we will do that in a later
step.  This is just to allow you to choose the configuration options you would
like to use for these items right now.
"""
	hostname = raw_input("What IP address or hostname is the DB server on?  [localhost] ") or "localhost"
	port = raw_input("What port is the DB server listening on? [5432] ") or "5432"
	dbname = raw_input("What name would you like to use for the database?  [moobot] ") or "moobot"
	username = raw_input("What username would you like to use to access the database? [moobot] ") or "moobot"
	password = raw_input("What password would you like to use for this user?  [moobot] ") or "moobot"

	print """
Excellent, these options will be permanently stored in your moobot
config file, so if you wish to alter these values later, you may simply
alter them there.
"""
	return (hostname, port, dbname, username, password)

def get_db_modules(module_list):
	valid_db_modules = ["MySQLdb", "PgSQL"]
	found_modules = []
	for module in valid_db_modules:
		if module in module_list:
			found_modules.append(module)
	return found_modules

def add_config_options(config_object, section, config_dict):
	config_object.add_section(section)
	for key in config_dict.keys():
		config_object.set(section, key, config_dict[key])
	return config_object


def main():
	# Wrap everything in a big ^C-handling loop
	try:
		# Greeting, wahoo.
		print_greeting()
		
		# If we got this far, we're probably going to create a config ...
		# unless they ^C out of it.  Regardless, we need to set up a
		# ConfigParser so we can write the config file out.
		#
		# Initialize a ConfigParser with the defaults
		new_config = ConfigParser.ConfigParser()

		# Step 1:
		# The module checking portion.
		found_modules = []
		do_module_check = prompt_for_module_checking()
		if do_module_check == 'y':
			found_modules = check_modules()
		print "Finished with: STEP 1 - Module checking"

		# Step 2A:
		# Configuration options.
		do_config = prompt_for_config()
		if do_config == 'y':
			config_dict = configure_bot()
		print "Finished with: STEP 2A - Bot configuration"
		
		# Now add the section to our configs
		this_section = "connection"
		new_config = add_config_options(new_config, this_section, config_dict)

		# Step 2B:
		# Database configuration

		# We may skip this step entirely if they have no DB modules to use.
		# We check and make sure that they do first before even bothering
		# them.
		avail_db_modules = get_db_modules(found_modules)
		if avail_db_modules != []:
			do_db_config = prompt_for_db_config()
			if do_db_config == 'y':
				config_dict = config_db_modules(avail_db_modules)
			print "Finished with: STEP 2B - Database configuration"

		# New section number two
		this_section = "database"
		new_config = add_config_options(new_config, this_section, config_dict)

		# Step 2C:
		# Modules configuration


		# Step 3:
		# Confirm choices

		# Step 4:
		# Write to file
		print "STEP 4 - Write config options to file"
		filename = raw_input("What filename would you like to save this to?  [moobot.conf] ") or "moobot.conf"
		new_config.write(file(filename, "w"))

	except KeyboardInterrupt:
		pass  # meh, these things happen :p
	except FailedRequiredModuleCheck:
		print_failed_module_check()

	print "Now exiting the installation program.  Thanks for choosing moobot for your IRC bot needs!"

if __name__ == "__main__":
	main()

# vim:nowrap:ts=4 sw=4 tw=78
