#!/usr/bin/env python
# -*- coding:utf-8 -*-

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
import url_codec, mars_codec, reverse_codec, leet_codec, pinyin_codec, split_codec
handler_list = ["encodeDecode", "russian_style"]

class encodeDecode(MooBotModule):
    def __init__(self):
        self.codecs = "(un|\\+|-)?(rot13|hex|base64|url\\+|url|mars|reverse|1337|py|split)"
        self.regex = "^(encode|decode|codec|%s)( .+?)?$" % self.codecs

    def usage(self, args):
        return self.msg_sender(args, "Usage: encode|decode|codec $encodings $string OR %s $string, $encodings is separated by | prefixed by optional + or -" % self.codecs)

    def handler(self, **args):
        txts = self.getRawArgs(args)

        cmd = txts[0]
        txts = txts[1:]
        if cmd == "encode" or cmd == "decode":
            if len(txts) < 2:
                return self.usage(args)
            encoding = txts[0]
            msg = ' '.join(txts[1:])
        elif cmd == "codec":
            if len(txts) < 2:
                return self.usage(args)
            encoding = txts[0]
            msg = ' '.join(txts[1:])
            cmd = "decode"
        else:
            if len(txts) < 1:
                return self.usage(args)
            msg = ' '.join(txts)
            encoding = cmd
            if encoding.lower().startswith("un"):
                encoding = encoding[2:]
                cmd = "decode"
            elif encoding.startswith('-'):
                encoding = encoding[1:]
                cmd = "decode"
            else:
                if encoding.startswith('+'):
                    encoding = encoding[1:]
                cmd = "encode"

        import re
        separator = re.compile("[|/,]")
        try:
            encodings = separator.split(encoding)
            for encoding in encodings:
                if encoding:
                    if encoding[0] == '+':
                        cmd = "encode"
                        encoding = encoding[1:]
                    elif encoding[0] == '-':
                        cmd = "decode"
                        encoding = encoding[1:]

                if cmd == "encode":
                    try:
                        msg = msg.encode(encoding)
                    except:
                        msg = msg.encode("utf8").encode(encoding)
                else:
                    if encoding == "hex":
                        msg = msg.replace("\\x", "").replace("\\X", "").replace(" ", "").replace("&#x", "").replace("&#X", "").replace(";", "")
                    try:
                        msg = str(msg)
                    except UnicodeEncodeError:
                        pass
                    msg = msg.decode(encoding)

            if type(msg) != unicode:
                cmd = "decode"
                try:
                    encoding = "utf8"
                    msg = msg.decode(encoding)
                except UnicodeDecodeError:
                    encoding = "gb18030"
                    msg = msg.decode(encoding)
        except Exception, e:
            msg = "Error \"%s\" when %s with '%s' encoding" % (e, cmd, encoding)

        return Event("privmsg", "", 
                     self.return_to_sender(args), [ msg ])

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
