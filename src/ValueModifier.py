#!/usr/bin/env python

class ValueModifier:
	def __init__(self, modifier, value):
		self.modifier = modifier
		self.value    = value

	def apply(self, value):
		if self.modifier == '+':
			return value + self.value
		elif self.modifier == '-':
			return value - self.value
		else:
			return self.value

class IntValueModifier(ValueModifier):
	"""
	>>> from ValueModifier import IntValueModifier
	>>> IntValueModifier("10").apply(15)
	10
	>>> IntValueModifier("-10").apply(15)
	5
	>>> IntValueModifier("+10").apply(15)
	25
	"""
	def __init__(self, intValueModifier):
		modifier = '='
		if len(intValueModifier) >= 2:
			modifier = intValueModifier[0]
			if modifier == '+' or modifier == '-':
				intValueModifier = intValueModifier[1:]
			else:
				modifier = '='

		# plain value
		ValueModifier.__init__(self, modifier, int(intValueModifier))

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
