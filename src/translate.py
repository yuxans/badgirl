#!/usr/bin/env python -*- coding:utf-8 -*-

# Copyright (c) 2002 Daniel DiPaolo, et. al.
# Copyright (c) 2006, 2007 FKtPp
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

import random
from irclib import Event
from irclib import Event
from moobot_module import MooBotModule
handler_list = ["reverse", "coding", "leet", "russian_style"]

class reverse(MooBotModule):
    def __init__(self):
        self.regex = "^reverse .+"

    def handler(self, **args):
        """gnirts a sesreveR"""

        orig_string = " ".join(args["text"].split(" ")[2:])
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

class russian_style (MooBotModule):
    """Graphic designers sometimes employ faux Cyrillic typography to
    give a Soviet or Russian feel to text, by replacing Latin letters
    with Cyrillic letters resembling them in appearance. A simple way
    to accomplish this is to replace capital letters R and N with
    Cyrillic Я and И for some"ЯUSSIAИ flavour". Other examples
    include Ш for W, Ц for U, Г for r, Ф for O, Д for A,
    and Ч or У for Y.
    """

    # TODO: fill in more cyrillic characters
    cyrillic_map = {u'R':u'Я', u'N':u'И', u'W':u'Ш', u'U':u'Ц', u'r':u'Г',
                    u'O':u'Ф', u'A':u'Д', u'Y':u'ЧУ'}
    
    def __init__ (self):
        self.regex = "^u?ru .+"

    def handler (self, **args):

        cmd, msg = args["text"].split(" ", 2)[1:]

        a2c = True
        
        if cmd.startswith('u'):
            a2c = False

        newmsg = []

        for each_char in msg:
            newmsg.append(self.trans_char(each_char, a2c))

        newmsg = ''.join(newmsg)

        return Event("privmsg", "", self.return_to_sender(args), [ newmsg ])
    
    def trans_char (self, source_char, ascii2cyrillic):
        """translate character acroding the translation map.

        source_char: the character(in unicode encoding) to be translated
        ascii2cyrillic: True for ascii to cyrillic translate, False
        for translate back.

        returns the translated character (in unicode encoding).

        >>> from translate import *
        >>> ru = russian_style()
        >>> ru.trans_char(u'A', True)
        u'\u0414'
        >>> ru.trans_char(u'\u0414', False)
        u'A'
        >>> ru.trans_char(u'\u0427', False)
        u'Y'
        >>> ru.trans_char(u'\u0423', False)
        u'Y'
        >>> ru.trans_char(u'X', True)
        u'X'
        >>> ru.trans_char(u'X', False)
        u'X'
        """
        dest_char = ''

        if ascii2cyrillic:
            # translate to cyrillic
            if self.cyrillic_map.has_key(source_char):
                maybe_multi_char = self.cyrillic_map[source_char]

                lindex = len (maybe_multi_char) - 1
                
                dest_char = lindex \
                            and maybe_multi_char[random.randint(0,lindex)] \
                            or maybe_multi_char
            else:
                dest_char = source_char

        else:
            # translate back to ascii
            for k in self.cyrillic_map.keys():
                if source_char in self.cyrillic_map[k]:
                    dest_char = k
                    break

            if not dest_char:
                dest_char = source_char
                
        return dest_char

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()

# vim:set ai sw=4 expandtab ts=4:
