#!/usr/bin/env python

# Copyright (c) 2002 Daniel DiPaolo, et. al.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

from irclib import Event
from irclib import Event
from moobot_module import MooBotModule
handler_list = ["reverse", "coding", "leet"]

class reverse(MooBotModule):
    def __init__(self):
        self.regex = "^reverse .+"

    def handler(self, **args):
        """gnirts a sesreveR"""

        orig_string = "".join(args["text"].split(" ")[2:])
        newstring = ""
        for i in range(1, len(orig_string)+1):
            newstring += orig_string[-i]
        return Event("privmsg", "", self.return_to_sender(args), [newstring])

class coding(MooBotModule):
    def __init__(self):
        self.regex = "^(rot13|u?(hex|base64)) .+"

    def handler(self, **args):

        cmd, msg = args["text"].split(" ", 2)[1:]

        if cmd.startswith("u"):
            cmd = cmd.lstrip("u")
            msg = msg.decode(cmd).decode('utf8')
        else:
            msg = msg.encode('utf8').encode(cmd)

        return Event("privmsg", "", 
                     self.return_to_sender(args), [ msg ])

class leet(MooBotModule):
    leetCharMap={"A":"/_\\", "B":"b", "C":"(", "D":"|)", "E":"e",
                 "F":"F", "G":"6", "H":"|-|", "I":"eye", "J":"j",
                 "K":"|{", "L":"L", "M":"|\\/|", "N":"|\\|",
                 "O":"()", "P":"P", "Q":"q", "R":"R", "S":"$",
                 "T":"7", "U":"|_|", "V":"\\/", "W":"\\/\\/",
                 "X":"><", "Y":"y", "Z":"z", "a":"4", "b":"8",
                 "c":"(", "d":"d", "e":"3", "f":"f", "g":"6",
                 "h":"h", "i":"1", "j":"j", "k":"k", "l":"|",
                 "m":"m", "n":"N", "o":"0", "p":"p", "q":"q",
                 "r":"r", "s":"5", "t":"7", "u":"U", "v":"V",
                 "w":"w", "x":"X", "y":"y", "z":"Z", " ":" "}
    leetWordMap={"you":"j00", "the":"teh", "your":"j00r",
                 "ever":"evar", "sucks":"soxz", "rocks":"roxz"}

    def __init__(self):
        self.regex = "^u?1337 .+"

    def handler(self, **args):

        cmd, msg = args["text"].split(" ", 2)[1:]

        if cmd.startswith("u"):
            msg = "LEET decode wasn't implemented yet"
        else:
            msg = self.leet_msg(msg)

        return Event("privmsg", "", self.return_to_sender(args), [ msg ])

    def leet_msg(self, msg):
        """Translate whole sentence to leet speaking

        Return the translated sentence.
        """
        word_list = []
        for word in msg.split(" "):
            tmp_word = self.leet_word(word)
            if not tmp_word:
                tmp_word = self.leet_char(word)
            word_list.append(tmp_word)
        return " ".join(word_list)

    def leet_word(self, word):
        """Translate a word to leet speaking by word

        return the leet word if successed, or return None"""
        if self.leetWordMap.has_key(word):
            return self.leetWordMap[word]
        else:
            return None

    def leet_char(self, word):
        """Translate a word to leet speaking by char

        return the leet word"""
        char_list = []
        for char in word:
            if self.leetCharMap.has_key(char):
                char_list.append(self.leetCharMap[char])
            else:
                char_list.append(char)
        return "".join(char_list)

# vim:set ai sw=4 expandtab ts=4:
