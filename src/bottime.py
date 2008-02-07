#!/usr/bin/env python

# Copyright (c) 2002 Brad Stewart
# Portions taken from Joe Wreschnig's DateTime.pm for Funbot.
#
# Copyright (C) 2008 by FKtPp
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

"""bottime.py - time-related modules """
import os
import time
import datetime

import database
from moobot_module import MooBotModule

handler_list=["cputime", "uptime", "date"]

class cputime(MooBotModule):
    def __init__(self):
        self.regex = "^cputime$"

    def handler(self, **args):
        """Reports CPU time usage for the current thread."""
        from os import times
        from irclib import Event
        target=args["channel"]
        if args["type"] == "privmsg":
            from irclib import nm_to_n
            target=nm_to_n(args["source"])
        return Event("privmsg", "", target,
                 ["User time: " + str(times()[0]) + " seconds, " + \
                  "system time: " + str(times()[1]) + " seconds.  "+\
                  "Childrens' user time: " + str(times()[2]) + ", "+\
                  "childrens' system time: " + str(times()[3])])

class uptime(MooBotModule):
    def __init__(self):
        self.regex = "^uptime$"
        self.pid = os.getpid()

        database.doSQL("DELETE FROM data WHERE type = 'uptime' AND " + \
                   "created_by != '" + str(self.pid) + "'");
        if len(database.doSQL("SELECT * FROM data WHERE " + \
                      "type = 'uptime' AND " + \
                      "created_by ='" + str(self.pid) + "'")) == 0:
            database.doSQL("INSERT INTO data (data, type, created_by) "+\
                       "VALUES('" + str(int(time.time())) + "', "+\
                       "'uptime', '" + str(self.pid) + "')")

    def handler(self, **args):
        from irclib import Event
        from seen import time2str
        start_time = database.doSQL("SELECT data FROM data WHERE " + \
                        "type = 'uptime' and " + \
                        "created_by ='" + str(self.pid) + \
                        "'")[0][0]
        result = "I've been awake for " + time2str(int(start_time))

        return Event("privmsg", "", self.return_to_sender(args), [ result ])

class date(MooBotModule):
    def __init__(self):
        self.regex = "^date(?:stz)?(?: [^ \t]+)?$"
        self.help_message_date = ""
        self.help_message_datestz = ""

    def handler(self, **args):
        import os
        from irclib import Event

        input = args["text"].lower().split().remove(0)
        request_nick = self.return_to_sender(args, select='nick')

        if input[0] == 'datestz':n
            result = self.handle_tz(input, request_nick)
        else:
            result = self.get_time(input, request_nick)

        return Event("privmsg", "", self.return_to_sender(args), \
                 [ result ])

    def get_time(self, input, request_nick):
        """return the requested time string

        .valid input list format:
        --------------
        [0]  [1]
        --------------
        date nick
        date +/-offset
        date help
        date
        --------------
        """
        assert input[0] == "date"

        tz_offset = None
        qnick = None

        if len(input) == 1:
            # No Parameter, we assume the user want to know his local time
            qnick = self.nick_validate(request_nick)

        elif len(input) == 2:
            tz_offset = self.tz_validate(input[1])
            if input[1] == "help":
                return self.help_message_date
            # if input[1] is not a valid tz_offset string, we assume it is 
            # a nick
            elif not tz_offset:
                qnick = self.nick_validate(input[1])
        else:
            return self.help_message_date

        if qnick:
            tz_offset1 = database.doSQL("select tz_offset from bottime "\
                                            "where nick = %s" % qnick)
        if tz_offset1:
            tz_offset = tz_offset1
        elif not tz_offset:
            return time.asctime()
        
        return = time.asctime(
            time.localtime(
                time.time() + (60 * 60 * tz_offset)
                )
            )


    def handle_tz(self, input, request_nick):
        """change or reset the time zone setting

        .valid input list format
        ----------------------
        [0]     [1]  [2]
        ----------------------
        datestz nick +/-offset
        datestz +/-offset
        ----------------------
        """
        assert input[0] == "datestz"

        tz_offset = None
        qnick = self.nick_validate(request_nick)

        if len(input) == 2:
            tz_offset = tz_validate(input[1])
        elif len(input) == 3:
            tz_offset = tz_validate(input[2])
            qnick = self.nick_validate(input[1])

        if not tz_offset:
            return self.help_message_datestz
        else:
            tmp_data = database.doSQL("select nick, tz_offset from bottime "\
                                          "where nick = %s" % qnick)

            if tmp_data:
                sql_string = "update bottime "\
                    "set tz_offset = %s "\
                    "where nick = %s" % (tz_offset, qnick)
            else:
                sql_string = "insert into bottime (nick, tz_offset) "\
                    "values (%s, %s)" % (qnick, tz_offset)

            database.doSQL(sql_string)

        return "done!"

    def tz_validate(self, tz_string):
        """validate the time zone offset string

        return the crosponding time zone offset if the tz_string is
        valid, or return False.
        """
        tz_offset = 0
        
        try:
            tz_offset = int(tz_string)
        except ValueError:
            return False

        if abs(tz_offset) > 12:
            return False

        return tz_offset

    def nick_validate(self, nick_string):
        """validate nick_string to prevent being SQL injected

        XXX this is a dummy function.
        """
        return nick_string
            
def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    
