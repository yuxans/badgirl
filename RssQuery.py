#!/usr/bin/env python

# Copyright (C) 2005 by FKtPp
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

"""RssQuery.py - query manage rssfeeds""" 
from moobot_module import MooBotModule
handler_list=["RssQuery"]

class RssRecord(MooBotModule):
	ttl = 3600
	keys = ["r_id","r_name","r_mtime","r_cache","r_url"]
	fields = ",".join(keys)
	datas = {}
	exists = False
	cached = False

	def getName(self):
		return self.datas["r_name"]

	def getUrl(self):
		return self.datas["r_url"]

	def _restore(self, datas):
		import time
		if not datas or not datas[0]:
			return False
		datas = datas[0]
		self.exists = True
		i = 0
		for key in self.keys:
			self.datas[key] = datas[i]
			i = i + 1
		if time.time() - int(self.datas["r_mtime"]) < self.ttl:
			self.cached = True
		return True

	def __init__(self, q, name = None):
		import database
		if q.find("://") != -1:
			key = "r_url"
		else:
			key = "r_name"
		feed = database.doSQL("SELECT %s FROM rss WHERE %s='%s'" % (
								self.fields, key, self.sqlEscape(q)))
		if self._restore(feed):
			pass
		elif name:
			database.doSQL("INSERT rss SET r_name='%s',r_url='%s'" % (
									self.sqlEscape(name), self.sqlEscape(q)
									))
			feed = database.doSQL("SELECT %s FROM rss WHERE r_name='%s'" % (
									self.fields, self.sqlEscape(name)))
			self._restore(feed)

	def delete(self):
		import database
		database.doSQL("DELETE FROM rss WHERE r_id=%d" % (
								int(self.datas["r_id"])
								))

	def getDatas(self):
		import urllib2, time, database, re, base64
		try:
			import cPickle as pickle
		except:
			import pickle

		if self.cached:
			data = base64.decodestring(self.datas["r_cache"])
			return pickle.loads(data)
		self.debug("open url")

		data = urllib2.urlopen(self.datas["r_url"]).read()
		encoding = "ISO-8859-1"
		m = re.compile('^<\\?xml[^>]*').search(data)
		if m:
			m = re.compile('encoding="([^"]+)"').search(m.group(0))
			if m:
				encoding = m.group(1)
				data = data.replace(m.group(0), "")

		data = data.decode(encoding.upper().replace("GB2312", "GBK"))

		# {{{ parse
		from RSS import ns, CollectionChannel, TrackingChannel
		from urllib2 import URLError

		#Create a tracking channel, which is a data structure that
		#Indexes RSS data by item URL
		tc = TrackingChannel()
		tc.encoding = None # unicode
		
		#Returns the RSSParser instance used, which can usually be ignored
		try:
			tc.parseString(data)
		except URLError, e:
			return [str(e)]
		except Exception, e:
			return "parse error"
		
		keys = {"title": (ns.rss10, 'title'),
				"link": (ns.rss10, 'link'),
				"description": (ns.rss10, 'description')}
		
		datas = {}
		for key in keys:
			datas[key] = []

		items = tc.listItems()
		for item in items:
			item_data = tc.getItem(item)
			for key in keys:
				datas[key].append(item_data.get(keys[key], "(none)"))
		# }}}

		data = pickle.dumps(datas)
		data = base64.encodestring(data)
		now = int(time.time())
		database.doSQL("UPDATE rss SET r_cache='%s',r_mtime='%s' WHERE r_id=%d" % (
								self.sqlEscape(data), now, int(self.datas["r_id"])
								))
		self.datas["r_cache"] = data
		self.datas["r_mtime"] = now
		self.cached = True
		return datas

	def getNames():
		import database
		rsses = database.doSQL("SELECT r_name FROM rss ORDER BY r_name")
		names = []
		for rss in rsses:
			names.append(rss[0])
		return names

	getNames = staticmethod(getNames)

	def flush():
		import database
		database.doSQL("UPDATE rss SET r_mtime=0,r_cache=''")

	flush = staticmethod(flush)

class RssQuery(MooBotModule):
	inqueries = {}

	def __init__(self):
		names = None # RssRecord.getNames()
		if names:
			names = "|" + "|".join(names)
		else:
			names = ""
		self.regex = "^((rss|rssflush|rssadd|rssdel) .+|rss%s)" % (names)

	def handler(self, **args):
		import string
		from irclib import Event
		import priv

		msg = "Huh?"

		dummy, cmd = args["text"].split(" ", 1)
		if cmd.find(" ") != -1:
			cmd, text = cmd.split(" ", 1)
		else:
			text = None

		cmd = cmd.lower()
		if cmd == 'rss' or cmd != 'rssadd' and cmd != 'rssdel' and cmd != 'rssflush':
			# add back
			if cmd != 'rss':
				text = cmd + " " + text

			if text:
				if text.find(' ') != -1:
					text, cmd = text.split(" ", 1)
					try:
						int(cmd)
						cmd = int(cmd)
					except:
						pass
				else:
					cmd = "no"
				rss = RssRecord(text)
				if not rss.exists:
					msg = "%s not exists" % text
				else:
					name = rss.getName()
					# no lock implemented yet
					error = None
					if self.inqueries.has_key(name):
						cmd = "busy"
					else:
						self.inqueries[name] = True
						try:
							datas = rss.getDatas()
						except Exception, e:
							error = e

						del self.inqueries[name]

					if error:
						msg = str(error)
					elif cmd == "busy":
						msg = "%s is already in query, please standby" % name
					elif cmd == "no":
						msg = text + ": " + " // ".join(datas['title'])[0:400]
					elif cmd == "url":
						msg = "%s: url is %s" % (text, rss.getUrl())
					elif cmd == 0:
						msg = "%s: count=%d" % (text, len(datas['link']))
					elif cmd:
						id = cmd - 1
						links = datas['link']
						if id < 0 or id > len(links):
							msg = "out of ubound"
						else:
							desc = datas['description'][id].split('<', 1)[0]
							desc = desc.split("\n", 1)[0]
							desc = desc.split("\r", 1)[0]
							msg = "%s: %s // %s // %s" % (text, links[id], datas['title'][id], desc)
			else:
				names = RssRecord.getNames() or "oops, None"
				msg = 'rss is "rss $key [|$num|url]" or "rssadd $key $url" or "rssdel $key" or "rssflush", where $key can be one of: ' + ", ".join(names)
		elif priv.checkPriv(args["source"], "rss") == 0:
			msg = "You don't have permission to do that."
		elif cmd == 'rssflush':
			RssRecord.flush()
			msg = "cache flushed"
		elif not text:
			msg = "params required"
		elif cmd == 'rssadd':
			try:
				name, url = text.split(" ", 1)
				rss = RssRecord(name)
				if rss.exists:
					msg = "%s is already exists" % name
				else:
					rss = RssRecord(url, name)
					msg = "%s added with url %s" % (name, url)
			except ValueError:
				msg = "error format"
			except:
				msg = "internal error"
		elif cmd == 'rssdel':
			name = text
			rss = RssRecord(name)
			if rss.exists:
				rss.delete()
				msg = "%s deleted" % name
			else:
				msg = "%s not exists" % name

		target = self.return_to_sender(args)
		result = Event("privmsg", "", target, [ "rss " + msg[0:500] ])
		return result
