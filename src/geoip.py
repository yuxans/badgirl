#!/usr/bin/env python
# -*- coding:gb2312 -*-

# Copyright (C) 2007 by FKtPp
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


import re, urllib
from irclib import Event
from moobot_module import MooBotModule

handler_list = ['chunzhen',]

class IEURLopener(urllib.FancyURLopener):
	version = "Mozilla/4.0 (compatible; MSIE 6.0)"

urllib._urlopener = IEURLopener()

class chunzhen(MooBotModule):
    """Get geographic location infomation of specific IP address from web.

    Query the infomation from http://www.cz88.net/ server, and pasre,
    print the result.
    """
    
    def __init__(self):
        """
	>>> import re, geoip
	>>> a = geoip.chunzhen()
	>>> r = re.compile(a.regex)
	>>> r.match('geoip ') and True or False
	False
	>>> r.match('geoip a') and True or False
	False
	>>> r.match('geoip a.') and True or False
	False
	>>> r.match('geoip a.b') and True or False
	False
	>>> r.match('geoip 1') and True or False
	False
	>>> r.match('geoip 1.') and True or False
	False
	>>> r.match('geoip 1.1') and True or False
	True
	>>> r.match('geoip 1.1.1') and True or False
	True
	>>> r.match('geoip 1.1.1.1') and True or False
	True
	>>> r.match('geoip 1.1.1.1.1') and True or False
	False
	>>> r.match('geoip 255.1.1.1') and True or False
	False
	>>> r.match('geoip 1.255.1.1') and True or False
	False
	>>> r.match('geoip 1.1.255.1') and True or False
	False
	>>> r.match('geoip 1.1.1.255') and True or False
	False
	>>> r.match('geoip 1.1.1.0') and True or False
	False
	>>> r.match('geoip 0.1.1.1') and True or False
	False
	>>> r.match('geoip 1.1.1.a') and True or False
	False
	>>> 
	"""
        # ipv4 pattern initialization
        num0_254 = '(?:25[0-4]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]?)'
        ipv4part = '(?:%s(?:\.%s){1,3})' % (num0_254, num0_254)

        self.regex='^geoip\s+%s$' % (ipv4part)

    def handler(self, **args):
        query_str = args["text"].split()

	query_str = query_str[2].strip()

	ipaddress = self.fixipv4(query_str)

        parms = urllib.urlencode({'ip':ipaddress})
        f = urllib.urlopen('http://www.cz88.net/ip/ipcheck.aspx', parms)

	geo_re = re.compile('document.write\("(.*)"\);')

	m = geo_re.search(f.read().decode('gbk'))
	
        geoinfo = (m and m.group(1) or 'Not Found')

        target = self.return_to_sender(args)
        result = Event('privmsg', '', target, [ ''.join(query_str, ': ', geoinfo)])

        return result

    def fixipv4(self, ipv4string):
        """fill the 3, 4 part of a particalarly typed ip address.

	fill '.0.1' if it has only two parts, fill '.1' if it has
	three parts, do nothing if it has all the four parts.

	>>> import geoip
	>>> a = geoip.chunzhen()
	>>> a.fixipv4('192.168')
	'192.168.0.1'
	>>> a.fixipv4('192.168.2')
	'192.168.2.1'
	>>> a.fixipv4('192.168.2.22')
	'192.168.2.22'
	>>> 
	"""

        parts = ipv4string.split('.')
        
        l = len(parts)

        if l == 2:
            parts.extend(['0','1'])
        elif l == 3:
            parts.extend(['1'])
        elif l == 4:
            pass
        else:
            # IP Error, length must be 2, 3, 4 or regexp must be wrong
            assert False
	    
        return '.'.join(parts)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
