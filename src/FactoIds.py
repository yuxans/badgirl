#!/usr/bin/env python

# Copyright (C) 2008 by mOo
# 
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

"""FactoIds.py -- FactoId data

Data management and help functions
"""

import database

def sqlEscape(text):
	""" escapes \ and 's in strings for SQL """

	text = text.replace("\\", "\\\\")
	text = text.replace('"', '\\"')
	text = text.replace("'", "\\'")
	return text

def get_token(text):
	""" gets the next token for SAR parsing from text """
	# Basically, this returns either:
	#  * one of the special_chars if it is the first character
	#  * otherwise, the string of non-special chars leading up
	#    to the first special char in the string
	special_chars = "()|"
	for length in range(len(text)):
		if text[length] in special_chars:
			# If we already have a string of chars going, back
			# up one and return that, we don't want to include
			# the special character we are currently on
			if length > 0:
				length -= 1
			# Once we hit a special character, break out of the
			# for loop so we can return
			break
	return text[:length+1]

def parseSar(text):
	import random
	stack = []
	# continue as long as text still has stuff in it
	while len(text) > 0:
		# get the first token from text
		token = get_token(text)

		# remove that token from text
		text = text[len(token):]

		# if the token is a ) and there is a ( in stack,
		# pop every element up to and including the (,
		# then chose one of those elements and append it
		# to stack.
		if token == ")" and "(" in stack \
		and "|" in stack[stack.index('('):]:
			choices = []
			while stack[-1] != "(":
				choices.append(stack.pop())

			stack.pop()
			chosen="|"
			while chosen == "|":
				chosen = random.choice(choices)

			if len(stack) > 0:
				if stack[-1] != "(" and stack[-1] != "|":
					stack.append(stack.pop() + chosen)
				else:
					stack.append(chosen)
			else:
				stack.append(chosen)

		elif token == "|":
			stack.append(token)
			if len(text) and (text[0] == "|" or text[0] == ")"):
				stack.append("")
		else:
			if len(stack) == 0 or stack[-1] == "|" \
			or stack[-1] == "(" or token == "(":
				stack.append(token)
			else:
				stack.append(stack.pop() + token)
	return "".join(stack)

from moobot import Debug
def getMaxValueLength():
	created_by = "factoid-length-check"
	top = 512	# 512 is the max chars in an IRC msg, from RFC
	bottom = 1
	while bottom < top:
		middle = int((top + bottom) / 2)
		factoid_key = "a" * middle
		Debug("%s %s %s" % (top, middle, bottom))
		try:
			sql = "insert into factoids(factoid_key, created_by) values('" + factoid_key + "', '" + created_by + "')"
			database.doSQL(sql)
			bottom = middle
		except:
			top = middle
			factoid_key = factoid_key[0:-1]
	length = middle

	Debug("Found length: %d" % length)
	database.doSQL("delete from factoids where created_by='" + created_by + "'")
	return length

fieldNames = ["requested_by", "requested_time",
              "requested_count", "created_by", "created_time", "modified_by",
              "modified_time", "locked_by", "locked_time"]
propertyNames = fieldNames
sqlFieldNames = ", ".join(fieldNames)

def _getByKey(fields, factoid_key, request_by = None):
	#  Query the database for the factoid value for the given key
	sql = "select %s from factoids "\
	        "where (factoid_key) = "\
	        "'%s'" % (fields, sqlEscape(factoid_key))
	result = database.doSQL(sql)

	if request_by:
		# Now that we are sure we have a factoid that got requested, increment
		# the count, set the new requester, etc.  NOTE: even for "literal"
		# requests, this is set.  Whether or not this is really is wanted is
		# ... debatable, but we don't really care.

		import time
		sql = "update factoids set "\
		        "requested_count = requested_count + 1, "\
		        "requested_by = '%s', "\
		        "requested_time = %s "\
		        "where (factoid_key) = '%s'" % (
		                sqlEscape(request_by), str(int(time.time())),
		                sqlEscape(factoid_key)
		                )
		database.doSQL(sql)

	if result:
		return result[0] # first row
	else:
		return None

def getFactoInfoByKey(factoid_key, request_by = None):
	row = _getByKey(sqlFieldNames, factoid_key, request_by)
	if row:
		factoInfo = {}
		i = 0
		for key in propertyNames:
			factoInfo[key] = row[i]
			i = i + 1
		return factoInfo
	else:
		return None

def getValueByKey(factoid_key, request_by = None):
	factoInfo = _getByKey("factoid_value", factoid_key, request_by)
	if factoInfo:
		return factoInfo[0] # return value
	else:
		return None

def exists(factoid_key):
	count = _getByKey("count(factoid_key)", factoid_key, None)
	if count[0]:
		return True
	else:
		return False

# return None for not found
def getLockedBy(factoid_key):
	factoInfo = _getByKey("locked_by", factoid_key, None)
	if not factoInfo:
		return None

	return factoInfo[0] or ""

# return None for not found
def getCreatedBy(factoid_key):
	factoInfo = _getByKey("created_by", factoid_key, None)
	if not factoInfo:
		return None

	return factoInfo[0] or ""

def getRandoms(count = 1):
	sql = "select factoid_key, factoid_value "\
	      "from factoids order by %s limit %d" % (database.getRandomFunction(), count)
	return database.doSQL(sql)

def add(factoid_key, factoid_value, request_by = None):
	import time
	sql = "insert into factoids("\
	      "factoid_key, factoid_value, created_by, created_time, "\
	      "requested_count) values ('%s', '%s', '%s', %s, 0)" % (
	                               sqlEscape(factoid_key),
	                               sqlEscape(factoid_value),
	                               request_by and sqlEscape(request_by) or 'me', str(time.time()))
	database.doSQL(sql)

def update(factoid_key, factoid_value, request_by = None):
	import time
	sql = "update factoids set factoid_value='%s', " \
	        "modified_time='%s', modified_by='%s' " \
	        "where (factoid_key)='%s'" % (
	        sqlEscape(factoid_value), str(time.time()), sqlEscape(requested_by),
	        sqlEscape(factoid_key))
	database.doSQL(sql)

def delete(factoid_key):
	database.doSQL("delete from factoids where factoid_key = '%s'" % sqlEscape(factoid_key))

def delete(factoid_key):
	_delete(factoid_key)
	database.doSQL("delete from factoidlink where linkfrom = '%s'" % sqlEscape(factoid_key))
	database.doSQL("delete from factoidlink where linkto   = '%s'" % sqlEscape(factoid_key))
	database.doSQL("delete from factoidlink where linktype = '%s'" % sqlEscape(factoid_key))

def replace(factoid_key, factoid_value, request_by = None):
	_delete(factoid_key)
	add(factoid_key, factoid_value, request_by)

def lock(factoid_key, request_by = None):
	sql = "update factoids "\
	      "set locked_by = '%s', "\
	      "locked_time = '%s' "\
	      "where (factoid_key) = '%s'" % (
	              request_by and sqlEscape(request_by) or 'me',
	              str(time.time()),
	              sqlEscape(factoid_key))
	database.doSQL(sql)

def unlock(factoid_key, request_by = None):
	sql = "update factoids "\
	      "set locked_by = NULL "\
	      "where (factoid_key) = '%s'" % (
	              self.sqlEscape(factoid_key.lower()))
	database.doSQL(sql)

def getLinkCreatedBy(linkfrom, linkto):
	sql = "select created_by from factoidlink"\
	      " where linkfrom = '%s' and linkto = '%s'" % (sqlEscape(linkfrom), sqlEscape(linkto))
	linkinfo = database.doSQL(sql)
	if not linkinfo:
		return None

	return linkinfo[0] or ""

def link(linkfrom, linkto, linktype, weight, request_by = None):
	unlink(linkfrom, linkto)
	import time
	sql = "insert into factoidlink("\
	      "linkfrom, linkto, linktype, weight, created_by, created_time)"\
	      " values ('%s', '%s', '%s', %s, '%s', %s)" % (
	                               sqlEscape(linkfrom),
	                               sqlEscape(linkto),
	                               sqlEscape(linktype),
	                               str(int(weight)),
	                               request_by and sqlEscape(request_by) or 'me', str(time.time()))
	database.doSQL(sql)

def unlink(linkfrom, linkto):
	import time
	sql = "delete from factoidlink" \
	      " where linkfrom = '%s'" \
	      " and linkto = '%s'" % (sqlEscape(linkfrom),
	                                sqlEscape(linkto))
	database.doSQL(sql)

def search(type, search_string, limit = 15, returnCount = False):
	# have type search the appropriate attribute in the database
	order = database.getRandomFunction()
	if type == "links":
		column = "linkto"
		order = "linktype,weight,linkto"
		table = "factoidlink"
		condition = "linkfrom = '%s'" % sqlEscape(search_string)
	elif type == "auth":
		table = "factoids"
		column = "created_by"
		condition = "created_by like '%s!%%'" % sqpEscape(search_string)
	else:
		table = "factoids"
		if type == "keys":
			column = "factoid_key"
		elif type == "values":
			column = "factoid_value"
		else:
			raise ValueError(type)
		condition = "%s like '%s'" % (column, '%' + sqlEscape(search_string) + '%')

	if returnCount:
		count = database.doSQL("select count(%s) from %s where %s" % (column, table, condition))[0][0]

	keys_query = "select " + column + \
	             " from " + table + \
	             " where " + condition + \
	             " order by " + order + \
	             " limit " + str(int(limit))

	keys = [row[0] for row in database.doSQL(keys_query)]

	if returnCount:
		return [keys, count]
	else:
		return keys
