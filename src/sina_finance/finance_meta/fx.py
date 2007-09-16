# -*- coding: utf-8 -*-

#####################################################################
# Meta data for forex
#####################################################################
# TODO: wtf is that unkown attr mean in sina??????????

from meta_map import FINANCE_META
from meta_map import COLOR

FINANCE_META['fx']={'cls':None,'attrs':None,'attr_types':None}

FINANCE_META['fx']['attrs']=['time','bid','ask','pre_close',
                         'unkown','open','high','low',
                         'last_price','name']
FINANCE_META['fx']['attr_types']={'time':str,'bid':float,'ask':float,'pre_close':float,
                             'unkown':int,'open':float,'high':float,'low':float,
                             'last_price':float,'name':unicode}

def to_hqstr_fx(self):
    """ Example: symbol='hkd' or 'HKD' ==> hqstr='HKD' """
    return self.symbol.upper()

def to_str_fx(self):
    change=self.last_price-self.pre_close
    pct= (self.pre_close != 0) and (change/self.pre_close)*100 or 0.0
    
    if pct ==0:
        color=COLOR.NORMAL
    elif pct>0:
        color=COLOR.RED
    else:
        color=COLOR.GREEN
    
    fmtstr=u"[%s] 名称: %s, 最新价:$c %.4f$n, 涨幅:$c %.4f%s$n, 昨收盘: %.4f, 今开盘: %.4f, 最低: %.4f, 最高: %.4f, 买入: %.4f, 卖出: %.4f, 时 间: %s"
    
    fmtstr=fmtstr.replace('$c',color).replace('$n',COLOR.NORMAL)
    
    return fmtstr%(self.symbol,self.name,self.last_price,pct,
                   '%',self.pre_close,self.open,self.low,
                   self.high,self.bid,self.ask,self.time)
