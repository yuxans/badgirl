#!/usr/bin/env python

# Copyright (c) 2002 Daniel DiPaolo 
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

import re
from moobot_module import MooBotModule
handler_list=["math"]

class math(MooBotModule):
    """Parses math expressions and returns the result"""
    def __init__(self):
        # Comment for the regexes:

        # Numbers:
        # \.\d+ : a number like ".023"
        # | : or
        # \d+(\.\d*)? : numbers like "1.23" or "10." or "1"
        # L? : ends in L or not
        number = "(\.\d+|\d+(\.\d*)?)L?"

        # Operands:
        # \(* : some or no leading parentheses
        # -? : negative (or not)
        #
        # number goes here
        #
        # \)* : some or no trailing parentheses
        operand = "(\(*-?" + number + "\)*)"

        # Operators:
        # [ : one of these single char operators
        #   % : modulus
        #   + : addition
        #   - : subtraction
        #   / : division
        #   * : multiplication
        # ]| : or
        # \*\* : exponentiation
        operator = "([%+-/*]|\*\*)"

        # Total regex:
        #
        # ^ : starts with
        # \s* : any amount of space, or none at all
        #
        # some operand
        #
        # \s* : some or no space after this
        # ( : and any number of operator/operand pairs after this
        #
        #   operator goes here
        #
        #   \s* : some or no spacing
        #
        #   operand goes here
        #
        #   \s* : any amount of trailing space, or none at all
        # )+ : one or more operator/number pairs
        # $ : must end here as well
        self.regex = "^\s*" + operand + "\s*(" + operator + "\s*" + operand + "\s*)+$"
    def handler(self, **args):
        from irclib import Event
        # Set target
        target = self.return_to_sender(args)
        
        # Split on spaces and then join everything after the first space
        # together -- this removes the botname
        expression = args["text"].split(" ")
        string = "".join(expression[1:])

        try:
            if not self.checkstarstar(string):
                raise ArithmeticError
            result = str(eval(string))
            if len(result) > 512:
                result = "I know the answer, but it's too long to say!"
        except OverflowError:
            result = "I don't have that many fingers and toes!"
        except ZeroDivisionError:
            result = "You can't divide by zero, stupid!"
        except FloatingPointError:
            result = "Floating point error."
        except ArithmeticError:
            result = "Arithmetic error."
        except SyntaxError:
            result = "Syntax error (remove leading 0's from non-octal numbers, and make sure parentheses are paired properly)"
        return Event("privmsg", "", target, [result])

    def checkstarstar(self, s):
        danger_operator = "\*\*"
        operator = "[()]"
        s_list = re.split(danger_operator, s)
        n = len(s_list)
        if n < 2:
            return True
        elif n > 2:
            return False
        else:
            number = re.split(operator, s_list[1])
            for x in number:
                if x != "" and eval(x) > 1000 :
                    return False
            return Ture
