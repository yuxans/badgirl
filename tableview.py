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

try:
   import gtk, GTK
except:
   print "Ths program uses PyGTK, which doesn't seem to be installed.\n"
   print "If you're using debian, apt-get install python-gtk,\n"
   print "otherwise, head on over to http://www.daa.com.au/~james/pygtk/\n"
   print "and grab it."


import database
from irclib import nm_to_n


class myProg:
	def __init__ (self, table):
		""" set up our program"""
		# Select the default table
		self.table = tables[table]
		# Create our window, then give it a title & border
		self.table_list = tables.keys()
		self.sort_column = 0
		self.sort_type = GTK.SORT_ASCENDING

		self.mainWind = gtk.GtkWindow()
		self.mainWind.set_title("Moobot Table Viewer")
		self.mainWind.set_border_width(10)

		# register the destroy method so the program shuts
		# down properly when someone hits the "X"-type-thingie
		self.mainWind.connect("destroy", self.destroy)

		# build and stick the vbox in our main window.
		self.build_vbox()
		self.mainWind.add(self.vbox)

		# finally, display our main window
		self.mainWind.show()

		self.populate_list()
	
	def build_vbox(self):
		#create vbox
		self.vbox = gtk.GtkVBox()

		# create a menu, a list box and a table with the buttons,
		# and stick 'em in our vbox.
		self.vbox.pack_start(self.init_menus(), expand=gtk.FALSE)
		self.vbox.pack_start(self.init_list())
		self.vbox.pack_end(self.init_table(), expand=gtk.FALSE)
		self.vbox.show()
	
	def mainloop(self):
		# run the gtk main loop, & let it do its thing.
		gtk.mainloop()
	
	def init_menus(self):
		accelGroup = gtk.GtkAccelGroup()
		itemFactory = gtk.GtkItemFactory(gtk.GtkMenuBar, "<main>", \
			accelGroup)
		self.mainWind.add_accel_group(accelGroup)
		menus = [
			('/_File',		None,	None,	0, '<Branch>'),
			('/_File/E_xit',	None,	self.process_file,	1, ''),
			('/_Table',		None,	None,	0, '<Branch>')
			]

		index = 0
		for tbl in self.table_list:
			menus.append(('/_Table/' + tbl, None, self.process_table, index, ''))
			index += 1

		itemFactory.create_items(menus)
		menubar = itemFactory.get_widget('<main>')
		menubar.show()
		return menubar

	def init_list(self):
		# create a scrolled window to stick our list
		# in
		scrolledWindow = gtk.GtkScrolledWindow()
		scrolledWindow.set_usize(600, 400)

		# create the list box
		self.listBox = gtk.GtkCList(len(self.table.headings), self.table.headings)
		self.listBox.show()
		self.listBox.connect("select_row", self.select)
		self.listBox.connect("click_column", self.sort)

		#stick the list into the scrolled window
		scrolledWindow.add_with_viewport(self.listBox)
		scrolledWindow.show()

		return scrolledWindow
	
	def init_table(self):
		""" set up the table containing all widgets """
		# create a table to line up our buttons for us
		t = gtk.GtkTable(rows = 2, cols = 1)

		# make a couple buttons & stick them in the table
                Reload = gtk.GtkButton('Requery')
		Reload.connect('clicked', self.reload)
                Quit = gtk.GtkButton('Quit')
		Quit.connect('clicked', self.destroy)
		Delete = gtk.GtkButton('Delete')
		Delete.connect('clicked', self.delete)

                t.attach(Delete, 1, 2, 0, 1, yoptions=0, xpadding=2, ypadding=2)
                t.attach(Reload, 0, 1, 1, 2, yoptions=0, xpadding=2, ypadding=2)
                t.attach(Quit, 1, 2, 1, 2, yoptions=0, xpadding=2, ypadding=2)

		# can't forget this ;)
		t.show_all()

		return t
	
	def populate_list(self):
		import string
		self.listBox.freeze()
		self.selected_index = -1
		for record in database.doSQL("select * from "+ self.table.name + " order by " + self.table.order_by):
			values=[]
			for index in self.table.order:
				values.append(string.replace(str(record[index]), "\\", "\\\\"))
			self.listBox.append(values)
		self.listBox.thaw()
		self.listBox.columns_autosize()

	
	def process_file(self, action, widget):
		if action == 1: self.destroy()

	def process_table(self, action, widget):
		if self.table != self.table_list[action]:
			self.mainWind.remove(self.vbox)
			self.table=tables[self.table_list[action]]
			self.build_vbox()
			self.mainWind.add(self.vbox)
			self.populate_list()


	def destroy(self, *args): 
		""" Clsoes the window and exists the program
		properly. """
		self.mainWind.hide()
		gtk.mainquit()
	
	def reload(self, *args):
		self.listBox.clear()
		self.populate_list()

	def select(self, *args):
		self.selected_index = args[1]

	def delete(self, *args):
		if self.selected_index != -1:
			fields = []
			for column in range(len(self.table.headings)):
				fields.append(self.listBox.get_text(self.selected_index, column))
			self.listBox.remove(self.selected_index)
			database.doSQL(self.table.makeSQL(fields))
		self.selected_index = -1
	
	def sort(self, *args):
		if args[1] != self.sort_column or self.sort_type != GTK.SORT_ASCENDING:
			self.listBox.set_sort_column(args[1])
			self.sort_column = args[1]
			self.listBox.set_sort_type(GTK.SORT_ASCENDING)
			self.sort_type = GTK.SORT_ASCENDING
		else:
			self.listBox.set_sort_type(GTK.SORT_DESCENDING)
			self.sort_type = GTK.SORT_DESCENDING
		self.listBox.sort()

	def test(self, *args):
		print args
	

class Table:
	def __init__ (self, name, headings, order, order_by, types):
		self.name = name
		self.headings = headings
		self.order = order
		self.order_by = order_by
		self.types = types

	def makeSQL(self, fields):
		sql = "delete from " + self.name + " where " 
		for index in range(len(fields)):
			if index > 0:
				sql += "and "
			sql += self.headings[index] + "="
			if self.types[index] == TEXT:
				sql += "'" + self.escape_special_chars(fields[index])  + "' "
			else:
				sql+= fields[index] + " "
		return sql
	
	def escape_special_chars(self,s):
		import string
		s = string.replace(s, "\\", "\\\\")
		s = string.replace(s, '"', '\\"')
		s = string.replace(s, "'", "\\'")
		return s
			


tables = {}
NUMBER = 0
TEXT = 1
tables["data"] = Table(
		"data", 
		["type", "data", "created_by"], 
		[1, 0, 2], 
		"type",
		[TEXT, TEXT, TEXT])

tables["grants"] = Table(
		"grants", 
		["priv_type", "hostmask"], 
		[1, 0], 
		"priv_type",
		[TEXT, TEXT])

tables["poll"] = Table(
		"poll", 
		["poll_num", "question"], 
		[1, 0], 
		"poll_num",
		[NUMBER, TEXT])

tables["stats"] = Table(
		"stats", 
		["type", "counter", "nick"], 
		[1, 2, 0], 
		"type, counter desc",
		[TEXT, NUMBER, TEXT])

tables["poll_options"] = Table(
		"poll_options", 
		["poll_num", "option_key", "option_text"], 
		[0, 1, 2], 
		"poll_num",
		[NUMBER, TEXT, TEXT])

tables["factoids"] = Table(
		"factoids", 
		["factoid_key", "factoid_value", "created_by", "requested_count"], 
		[0, 10, 4, 3], 
		"factoid_key",
		[TEXT, TEXT, TEXT, NUMBER])

tables["seen"] = Table(
		"seen", 
		["nick", "time", "message"], 
		[0, 2, 3], 
		"nick",
		[TEXT, NUMBER, TEXT])

tables["webstats"] = Table(
		"webstats", 
		["nick", "count", "quote"], 
		[0, 1, 2], 
		"count desc",
		[TEXT, NUMBER, TEXT])

def main():
	
	j = myProg("grants")
	j.mainloop()

main()
