#!/usr/bin/env python

#     Copyright 2003 Phil Gregory <phil_g@pobox.com>
# 
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have be able to view the GNU General Public License at 
#     http://www.gnu.org/copyleft/gpl.html ; if not, write to the Free Software
#     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


"""urlgrab.py - Grabs URLs and stores them for later perusal."""

handler_list=["url", "outgoingurl"]

from moobot_module import MooBotModule
from moobot import Handler
from irclib import Event, nm_to_n, is_channel
import re, database
import titlefetcher
import hashlib
import urlparse

# Don't ask.  I might tell you.  ;)
urlregex = '[a-z][a-z0-9+-]*://(((([-a-z0-9_.!~*\'();:&=+$\,]|%[0-9a-f][0-9a-f])*@)?((([a-z0-9]([a-z0-9-]*[a-z0-9])?)\.)*([a-z]([a-z0-9-]*[a-z0-9])?)\.?|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)(:[0-9]+)?)|([-a-z0-9_.!~*\'()$\,;:@&=+]|%[0-9a-f][0-9a-f])+)(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*)*)?(\?([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?(#([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?|www\.(([a-z0-9]([a-z0-9-]*[a-z0-9])?)\.)*([a-z]([a-z0-9-]*[a-z0-9])?)\.?(:[0-9]+)?(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*)*)?(\?([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?(#([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?'

class urlGrabber(MooBotModule):
	rUrl = re.compile(urlregex, re.I)
	rWhiteSpaces = re.compile("\\s+", re.S)
	imageExts = 'gif|tif|tiff|jpe|jpg|jpeg|png|bmp'
	rImageUrl = re.compile("^[^?]+\.(%s)$" % imageExts, re.I)
	mediaExts = imageExts + 'dib|z|tgz|gz|zip|rar|7z|arj|wav|midi|mid|mka|mpa|mp2|m1a|m2a|mp3|wma|rm|rmvb|avi|xvid|div|dss|dsa|dsv|dsm|ac3|dts|ifo|vob|mka|mkv|mpg|mpeg|mpe|m1v|m2v|mpv2|mp2v|ts|tp|mp4|m4v|m4b|hdmov|3gp|3gpp|mpc|ogm|ogg|asx|m3u|pls|wvx|wax|wmx|mpcpl|mov|qt|amr|3g2|3gp2|ram|wmv|wmp|asf|bin|hex|qx|ar'
	rMediaUrl = re.compile("^[^?]+\.(%s)$" % mediaExts, re.I)

	def addHost(self, scheme, host, port):
		sql = "INSERT IGNORE urlhost(scheme,host,port) VALUES('%s','%s',%d)" % (self.sqlEscape(scheme), self.sqlEscape(host), int(port))
		database.doSQL(sql)
		return self.getHostId(scheme, host, port)

	def getHostId(self, scheme, host, port):
		sql = "SELECT hostid FROM urlhost WHERE scheme='%s' AND host='%s' AND port=%d" % (self.sqlEscape(scheme), self.sqlEscape(host), int(port))
		ret = database.doSQL(sql)
		if ret and ret[0]:
			return ret[0][0]

	def addChan(self, name):
		sql = "INSERT IGNORE chan(name) VALUES('%s')" % self.sqlEscape(name)
		database.doSQL(sql)
		return self.getChanId(name)

	def getChanId(self, name):
		sql = "SELECT chanid FROM chan WHERE name='%s'" % self.sqlEscape(name)
		ret = database.doSQL(sql)
		if ret and ret[0]:
			return ret[0][0]

	def urlHash(self, url):
		return hashlib.md5(url.encode("utf8", "ignore")).hexdigest()

	def getUrl(self, url, hash):
		sql = "SELECT urlid,title FROM url WHERE url='%s' AND hash='%s'" % (self.sqlEscape(url), self.sqlEscape(hash))
		ret = database.doSQL(sql)
		if ret and ret[0]:
			return ret[0]
		else:
			return (None, None)

	def addUrl(self, url, hash, source, target, str):
		id, title = self.getUrl(url, hash)
		if id:
			if not title:
				title = self.fetchTitle(url)
				if title:
					database.doSQL("UPDATE url SET title='%s' WHERE url='%s' AND hash='%s'" % (self.sqlEscape(title), self.sqlEscape(url), self.sqlEscape(hash)))

			return title

		urlInfo = urlparse.urlparse(url)
		scheme = urlInfo.scheme
		port = urlInfo.port
		if not port:
			if scheme == 'http':
				port = 80
			elif scheme == 'https':
				port = 443

		host = urlInfo.hostname
		if not host:
			return

		hostId = self.addHost(scheme, host, port)
		chanId = 0
		if is_channel(target):
			chanId = self.addChan(target[1:])

		# Strip mIRC color codes
		str = re.sub('\003\d{1,2},\d{1,2}', '', str)
		str = re.sub('\003\d{0,2}', '', str)
		# Strip mIRC bold, plain, reverse and underline codes
		str = re.sub('[\002\017\026\037]', '', str)

		values = {}

		values["nickid"]   = "%d"   % int(self.addNick(nm_to_n(source)))
		values["string"]   = "'%s'" % self.sqlEscape(str)
		values["url"]      = "'%s'" % self.sqlEscape(url)
		values["hash"]     = "'%s'" % self.sqlEscape(hash)
		values["hostid"]   = "%d"   % int(hostId)
		values["chanid"]   = "%d"   % int(chanId)
		values["time"]     = "CURRENT_TIMESTAMP()"
		values["type"]     = "'%s'" % self.sqlEscape(self.rImageUrl.search(url) and "image" or "html")

		if database.type == "mysql":
			pass
		elif database.type == "pgsql":
			values['time'] = 'CURRENT_TIMESTAMP'
		elif database.type == "sqlite3":
			values['time'] = 'time()'

		title = self.fetchTitle(url) or ""

		values['title'] = "'%s'" % self.sqlEscape(title)

		sql = "insert into url(%s) values(%s)" % (','.join(values.keys()), ','.join(values.values()))
		database.doSQL(sql)
		return title

	def fetchTitle(self, url):
		if not self.rMediaUrl.search(url):
			try:
				title = titlefetcher.fetch(url)
				if title:
					title = self.rWhiteSpaces.sub(" ", title).strip()
					return title
			except titlefetcher.UnimplementedProtocol:
				pass
		else:
			print self.rMediaUrl.search(url).group(0)

	def matchUrl(self, str):
		match = self.rUrl.search(str)
		if match:
			url = match.group(0).split('#', 1)[0].rstrip(',.')
			return url

class url(urlGrabber):
	regex = urlregex
	type = Handler.GLOBAL
	priority = -15

	def handler(self, **args):
		"""Looks for urls in each line of text."""

		ret = []
		url = self.matchUrl(args["text"])
		bot = args["ref"]()
		try:
			showTitle = int(bot.configs["urlgrab"]["showtitle"])
		except KeyError:
			showTitle = True
		except ValueError:
			showTitle = False

		if url:
			title = None
			hash = self.urlHash(url)

			rows = database.doSQL(
				"""SELECT seen.nick,chan.name,url.time,url.title
				FROM url
				LEFT JOIN seen ON seen.nickid=url.nickid
				LEFT JOIN chan ON chan.chanid=url.chanid
				WHERE url='%s' AND hash='%s' AND length(title) > 0""" % (url, hash))
			if rows and rows[0]:
				nick, chan, timestamp, title = rows[0]
				if len(nick) > 2:
					nick = nick[0] + "/" + nick[1:]
				msg = u'[%s] Posted by %s@%s already: %s' % (timestamp, nick, chan, title)
				if showTitle:
					ret.append(self.msg_sender(args, msg))
			else:
				title = self.addUrl(url, hash, args["source"], args["channel"], args["text"])
				if title and showTitle:
					ret.append(self.msg_sender(args, title))

		ret.append(Event("continue", "", "", [ ]))
		return ret


# This class is to catch URLs in what the bot says.
class outgoingurl(urlGrabber):
	type = "privmsg"
	priority = -15

	def handler(self, **args):
		"""Looks for urls in text the bot sends."""
		import re

		event = args["event"]
		str = " ".join(event.arguments())
		# Only things to channels are used.  Nothing private.  And, of course,
		# we need to check to see if the line actually contains a URL.
		url = self.matchUrl(str)
		if url:
			if event.target().startswith("#"):
				self.addUrl(url, self.urlHash(url), event.source(), event.target(), str)
			
		return Event("continue", "", "", [ ])
