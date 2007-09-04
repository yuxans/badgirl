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

from moobot_module import MooBotModule
handler_list=["convert"]

class convert(MooBotModule):
    """Parses unit conversion requests and returns the response
       Author: jamessan"""
    def __init__(self):
        # Conversion Dictionary
        # F->C = (T-32)*5/9
        # F->R = T-459.69
        # C->K = T+273.15
        self.conv_dict= {
		"m" : { "mm" : "1000.", "cm" : "100.", "km" : ".001",
			"in" : "(100/2.54)", "ft" : "(100/2.54/12)",
			"yd" : "(100/2.54/12/3)", "mi" : "(100/2.54/12/5280)"},
		"kg" : { "g" : "1000.", "lb" : "2.20459", "oz" : "35.27344" },
		"L" : { "mL" : "1000.", "gal" : "(125/473.176)" }}
        # Comment for the regexes:

        # Numbers:
        # \.\d+ : a number like ".023"
        # | : or
        # \d+(\.\d*)? : numbers like "1.23" or "10." or "1"
        # L? : ends in L or not
        number = "(\.\d+|\d+(\.\d*)?)L?"


        # Operands:
        # -? : negative (or not)
        operand = "(-?" + number + ")"


        # Units:
        # Any sequence of alphanumeric characters.  Later procedures will
        # complain if it's an invalid unit.
        units = "([A-Za-z0-9-\^]+)"


        #self.distances = "(mm|cm|m|km|in|ft|yd|mi)"
        self.temps = "(C|F|K|R)"	
        #self.weights = "(g|kg|lb|oz)"
        #self.volumes = "(ml|l|gal)"


        # Total regex:
        #
        # ^ : starts with
        # \s* : any amount of space, or none at all
        #
        # the command, with previously-defined regexes for numbers and units
        # 
        # \s* : any amount of trailing space, or none at all
        # $ : must end here as well
        self.regex = "^\s*convert " + operand + " from " + units + " to " + units + "\s*$"

    def handler(self, **args):
        from irclib import Event
        import os, re
        # Set target
        target = self.return_to_sender(args)
        
        # Split on spaces and then join everything after the first space
        # together -- this removes the botname
        expression = re.split('\s+', args["text"])[2:]


        if os.path.exists("/usr/bin/units"):
            # Scrub the arguments for paranoia's sake.
            number    = re.sub('[^0-9.]', '', expression[0]);
            from_unit = re.sub('[^A-Za-z0-9-]', '', expression[2]);
            to_unit   = re.sub('[^A-Za-z0-9-]', '', expression[4]);
            units = os.popen("/usr/bin/units -- '" + number + " " + from_unit + "' '" + \
                             to_unit + "'")
            message = units.readline()
            message = re.sub('^\s+\* ', '', message);
        else:
            message = self.handle_expression(expression)

        return Event("privmsg", "", target, [ message ])
        
    def handle_expression(self, expression):
        import re
        
        number=expression[0]
        from_unit=expression[2]
        to_unit=expression[4]
        
        if from_unit == to_unit:
            return "If you can't convert to the same unit of measurement, you need more help than I can give"
        string=""
        if not re.search(from_unit,self.temps):
            try:
                if self.conv_dict.has_key(from_unit):
                    string=number+"*"+self.conv_dict[from_unit][to_unit]
                elif self.conv_dict.has_key(to_unit):
                    string=number+"/"+self.conv_dict[to_unit][from_unit]
                elif self.conv_dict["m"].has_key(from_unit):
                    number=str(eval(number+"/"+self.conv_dict["m"][from_unit]))
                    string=number+"*"+self.conv_dict["m"][to_unit]
                elif self.conv_dict["kg"].has_key(from_unit):
                    number=str(eval(number+"/"+self.conv_dict["kg"][from_unit]))
                    string=number+"*"+self.conv_dict["kg"][to_unit]
                elif self.conv_dict["L"].has_key(from_unit):
                    number=str(eval(number+"/"+self.conv_dict["L"][from_unit]))
                    string=number+"*"+self.conv_dict["L"][to_unit]
                else:
                    return "I don't recognize those units"
            except KeyError:
                return "What are you, dumb? You can't convert between those units."
        elif re.search(to_unit,self.temps):
            if from_unit == "K":
                number=str(eval(number+"-273.15"))
            elif from_unit == "R":
                number=str(eval("("+number+"-459.69-32)*5./9"))
            elif from_unit == "F":
                number=str(eval("("+number+"-32)*5./9"))
            if to_unit == "C":
                string=number
            elif to_unit == "F":
                string=number+"*9./5+32"
            elif to_unit == "K":
                string=number+"+273.15"
            elif to_unit == "R":
                string=number+"*9./5+32+459.69"
        else:
            return "What are you, dumb? You can't convert between those units"
        
        try:
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
        print result
        return result
