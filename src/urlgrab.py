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

# Don't ask.  I might tell you.  ;)
urlregex = '[a-z][a-z0-9+-]*://(((([-a-z0-9_.!~*\'();:&=+$\,]|%[0-9a-f][0-9a-f])*@)?((([a-z0-9]([a-z0-9-]*[a-z0-9])?)\.)*([a-z]([a-z0-9-]*[a-z0-9])?)\.?|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)(:[0-9]+)?)|([-a-z0-9_.!~*\'()$\,;:@&=+]|%[0-9a-f][0-9a-f])+)(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*)*)?(\?([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?(#([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?|www\.(([a-z0-9]([a-z0-9-]*[a-z0-9])?)\.)*([a-z]([a-z0-9-]*[a-z0-9])?)\.?(:[0-9]+)?(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*)*)?(\?([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?(#([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?'


class url(MooBotModule):
    def __init__(self):
        self.regex = urlregex
        self.type = Handler.GLOBAL
        self.priority = -15

    def handler(self, **args):
        """Looks for urls in each line of text."""

        addurl(self, args["source"], args["text"])
        
        from irclib import Event
        return Event("continue", "", "", [ ])


# This class is to catch URLs in what the bot says.
class outgoingurl(MooBotModule):
    def __init__(self):
        self.type = "privmsg"
        self.priority = -15

    def handler(self, **args):
        """Looks for urls in text the bot sends."""
        import re

        event = args["event"]
        str = "".join(event.arguments())
        # Only things to channels are used.  Nothing private.  And, of course,
        # we need to check to see if the line actually contains a URL.
        if (re.search('^#', event.target()) and re.search(urlregex, str)):
            addurl(self, event.source(), str)
            
        from irclib import Event
        return Event("continue", "", "", [ ])


def addurl(obj, source, str):
    from irclib import nm_to_n
    import re, database
    
    # Strip mIRC color codes
    str = re.sub('\003\d{1,2},\d{1,2}', '', str)
    str = re.sub('\003\d{0,2}', '', str)
    # Strip mIRC bold, plain, reverse and underline codes
    str = re.sub('[\002\017\026\037]', '', str)
            
    if database.type == "mysql":
        insert_query = "INSERT INTO url (nick, string) " \
                       "VALUES ('%s', '%s')" % (
            obj.sqlEscape(nm_to_n(source)), obj.sqlEscape(str))
    elif database.type == "pgsql":
        insert_query = "INSERT INTO url (nick, string, time) " \
                       "VALUES ('%s', '%s', CURRENT_TIMESTAMP)" % (
            obj.sqlEscape(nm_to_n(source)), obj.sqlEscape(str))
    
    database.doSQL(insert_query)
