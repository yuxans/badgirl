#!/usr/bin/env python
"""utilities.py - Functions used in moobot modules that may useful elsewhere,
and don't really belong in a specific module."""

ESCAPE = "\33"
RED = ESCAPE + "[31m"
GREEN = ESCAPE + "[32m"
YELLOW = ESCAPE + "[33m"
BLUE = ESCAPE + "[34m"
PURPLE = ESCAPE + "[35m"
NORMAL = ESCAPE + "[0m"
UNDERLINE = ESCAPE + "[4m"
BLINK = ESCAPE + "[5m"

import re
trimRegex = re.compile("^\s+|\s+$")
ltrimRegex = re.compile("^\s+")
rtrimRegex = re.compile("\s+$")

def trim(s):
	"""
	>>> from utilities import *
	>>> trim("  -  ")
	'-'
	"""
	return trimRegex.sub("", s)

def ltrim(s):
	"""
	>>> from utilities import *
	>>> ltrim("  -  ")
	'-  '
	"""
	return ltrimRegex.sub("", s)

def rtrim(s):
	"""
	>>> from utilities import *
	>>> rtrim("  -  ")
	'  -'
	"""
	return rtrimRegex.sub("", s)

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
