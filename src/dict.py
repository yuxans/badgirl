#!/usr/bin/env python

# Copyright (C) 2005 by moo

from moobot_module import MooBotModule

maxsearch = 30
def sqlEscape(text):
	""" escapes \ and 's in strings for SQL """
	import string
	text = string.replace(text, "\\", "\\\\")
	text = string.replace(text, '"', '\\"')
	text = string.replace(text, "'", "\\'")
	return text

def lookup(dk):
	import database
	rs = database.doSQL("SELECT d_value FROM dict WHERE d_key='%s'" % sqlEscape(dk))
	try:
		return rs[0][0] or False
	except:
		return False

def search(dk):
	global maxsearch
	import database
	rs = database.doSQL("SELECT d_key FROM dict WHERE d_key LIKE '%s' LIMIT %d" % (dk.replace('*', '%').replace('?', '_'), maxsearch))
	try:
		ret = []
		c = len(rs)
		i = 0
		while i < c:
			ret.append(rs[i][0])
			i += 1

		return ret or False
	except:
		return False
