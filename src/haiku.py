#!/usr/bin/env python

# Originally based on idea (and, sadly, lost implementation) by Don Marti.
# Requires the c06d file from  http://www.speech.cs.cmu.edu/cgi-bin/cmudict
#
# Further hacked by Phil Gregory to fit into the moobot framework.
#
# Original Python version at http://www.oblomovka.com/code/
#
#     Copyright 2002 Danny O'Brien <danny@spesh.com>
#     Copyright 2002 Phil Gregory <phil_g@pobox.com>
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
#
#     "One person gains one
#     dollar by destroying two
#     dollars' worth of wealth."

"""haiku.py - Looks for accidental haiku."""

handler_list=["haiku"]

from moobot_module import MooBotModule
from moobot import Handler

class haiku(MooBotModule):
    def __init__(self):
        self.regex = "."
        self.type = Handler.GLOBAL
        self.priority = -15

    def handler(self, **args):
        """Looks for haiku in each line of text.  If found, mentions the haiku
        to the channel."""
        from irclib import Event
        result = check_for_haiku(args["text"])
        if (result != ""):
            from irclib import nm_to_n
            return [ Event("privmsg", "", self.return_to_sender(args),
                           [ result + "  -- a haiku by " + nm_to_n(args["source"]) ]),
                     Event("continue", "", "", [ ])]
		return Event("continue", "", "", [])


import sys, os, re

GUESS = 1
trycmu = ['/usr/local/share/c06d', '/usr/share/dict/c06d', 'c06d' ]
haiku_form = ( 5, 7, 5 )
sy_dict = {}

def get_sy_count(word):
    """Return the number of syllables in word, 0 if word not recognised """
    uword = re.sub('[^A-Z\']','',word.upper())
    if (uword == ''): return 0
    if uword in sy_dict.keys(): return sy_dict[uword] # memoize
    if cmudict:
        cdu = re.split(r'\s+', os.popen('/bin/egrep "^%s " %s' % (uword,cmudict)).readline(), 1)
        if (cdu[0] != uword):
            sy_count = 0
        else:
            sy_count = len(re.findall("\d+", cdu[1]))
        if sy_count == 0 and (GUESS == 1):
            sy_count = guess_sy_count(word)
    else:
        sy_count = guess_sy_count(word)
    sy_dict[uword] = sy_count
    return sy_count
    

SubSyl = [
       'cial',
       'tia',
       'cius',
       'cious',
       'giu',              # belgium!
       'ion',
       'iou',
       'sia$',
       '.ely$',             # absolutely! (but not ely!)
      ]

AddSyl = [ 
       'ia',
       'riet',
       'dien',
       'iu',
       'io',
       'ii',
       '[aeiouym]bl$',     # -Vble, plus -mble
       '[aeiou]{3}',       # agreeable
       '^mc',
       'ism$',             # -isms
       '([^aeiouy])\1l$',  # middle twiddle battle bottle, etc.
       '[^l]lien',         # alien, salient [1]
           '^coa[dglx].',      # [2]
       '[^gq]ua[^auieo]',  # i think this fixes more than it breaks
       'dnt$',           # couldn't
      ]

def guess_sy_count(word):
    """If we can't lookup the word, then guess its syllables. This is
    based on Greg Fast's Perl module Lingua::EN::Syllables"""
    mungedword = re.sub('e$','',word.lower())
    splitword = re.split(r'[^aeiouy]+', mungedword)
    splitword = [ x for x in splitword if (x != '') ]
    syllables = 0
    for i in SubSyl:
        if re.search(i,mungedword):
            syllables -= 1
    for i in AddSyl:
        if re.search(i,mungedword):
            syllables += 1
    if len(mungedword) == 1: syllables =+ 1
    syllables += len(splitword)
    if syllables == 0: syllables = 1
    print "Guess:", syllables, word
    return syllables

def pp_haiku(list):
    """Pretty-print a list made up lists of lists of word syllable pairs as a
    human-readable verse."""

    lines = []

    for a in list:
        lines.append("".join(a))
    return " / ".join(lines)


cmudict=''
for i in trycmu:
    if (os.path.exists(i)):
        cmudict = i
        break
if (cmudict == ''):
    print >> sys.stderr,  'Could not find %s the Carnegie Mellon Pronunciation Dictionary' % trycmu[-1]
    print >> sys.stderr,  'Will try and guess syllable counts instead. No guarantees!'


def check_for_haiku(line):
    full_haiku = []
    haiku_line = []
    form_line = 0
    sy_count = 0
    failed = 0
    result = ""

    w = re.split(r'\s+', line)
    for word in w:
        if (form_line > 2):
            failed = 1
            break
        
        word_sy = get_sy_count(word)
        sy_count = sy_count + word_sy
        if (word_sy > 0):
            haiku_line.append(word)

        if (sy_count == haiku_form[form_line]):   # have line?
            full_haiku.append(haiku_line)
            haiku_line = []
            form_line = form_line + 1
            sy_count = 0
        elif (sy_count > haiku_form[form_line]):
            failed = 1
            break

    if (form_line > 2 and not failed):
        result = pp_haiku(full_haiku)

    return result
