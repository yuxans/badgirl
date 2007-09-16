# -*- coding: utf-8 -*-


import re
from singleton import Singleton
from finance_meta import *


class FinanceItem(object):
    def __init__(self,flag=None,symbol=None,name=None,**kwargs):
        if kwargs.has_key('sugg_str'):
            flag,symbol,name=kwargs['sugg_str'].split('-')
        # fill the attrs with default values
        for attr,attr_type in self.attr_types.items():
            self.__setattr__(attr,attr_type())
        self.flag=flag
        self.symbol=symbol
        self.name=name
    
    def feed(self,rawdata):
        values=rawdata.split(',')
        num_of_values=len(values)
        slots=self.__slots__
        attr_types=self.attr_types
        if len(slots)==num_of_values:
            for i in range(num_of_values):
                attr,vstr =  slots[i], values[i]
                attr_type=attr_types[attr]
                value=None
                try:
                    value=( vstr=='' ) and attr_type() or attr_type(vstr)
                except:
                    # use default
                    value=attr_type()
                self.__setattr__(attr,value)
            return True
        else:
            return False
        
    def to_hqstr(self): pass

#####################################
# ***Generate the actual finance items classes from the meta data. 
for flag,v in FINANCE_META.items():
    clsdict={}
    clsdict['__slots__']=v['attrs']
    clsdict['attr_types']=v['attr_types']
    clsdict['to_hqstr']=eval('to_hqstr_'+flag)
    clsdict['__str__']=eval('to_str_'+flag)

    v['cls']=type('Item_'+flag, (FinanceItem,), clsdict)
    del clsdict
######################################


class FinanceItemFactory(Singleton):
    HQSTR_PATT=re.compile(r'^[a-z]+-[a-z0-9]+-.*$', re.I)
    def create(self,sugg_str):
        if sugg_str!=None and FinanceItemFactory.HQSTR_PATT.match(sugg_str):
            flag,symbol,name=sugg_str.split('-')
            if flag in FINANCE_META.keys():
                cls=FINANCE_META[flag]['cls']
                return cls(flag,symbol,name)
        return None

if __name__=='__main__':
    ff=FinanceItemFactory()
    hk=ff.create('hk-0998-c')
    sh=ff.create('sh-600001-HD')
    sz=ff.create('sz-000001-SF')
    print hk.to_hqstr(),hk
    print sh.to_hqstr(),sh
    print sz.to_hqstr(),sz
