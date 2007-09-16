# -*- coding: utf-8 -*-

#####################################################################
# Meta data for HK stocks
#####################################################################

from meta_map import FINANCE_META
from meta_map import COLOR

FINANCE_META['hk']={'cls':None,'attrs':None,'attr_types':None}

FINANCE_META['hk']['attrs']=['eng_name','chs_name','open','pre_close',
                         'high','low','last_price','price_change',
                         'pct_change','bid','ask','turnover',
                         'volume','pe','yield','high_52w','low_52w',
                         'date','time']
FINANCE_META['hk']['attr_types']={'eng_name':str,'chs_name':unicode,'open':float,'pre_close':float,
                             'high':float,'low':float,'last_price':float,'price_change':float,
                             'pct_change':float,'bid':float,'ask':float,'turnover':float,
                             'volume':int,'pe':float,'yield':float,'high_52w':float,'low_52w':float,
                             'date':str,'time':str}
def to_hqstr_hk(self):
    """ Example: flag='hk', symbol='3986' ==> hqstr='hk3986' """
    return self.flag+self.symbol

def to_str_hk(self):
    
    if self.pct_change ==0:
        color=COLOR.NORMAL
    elif self.pct_change>0:
        color=COLOR.RED
    else:
        color=COLOR.GREEN
    
    fmtstr=u"[%s] 股票名称: %s, 当前价:$c %.2f$n, 涨幅:$c %.2f%s$n, 成交量 %d, 昨收盘: %.2f, 今开盘: %.2f, 最低: %.2f, 最高: %.2f, 时 间: %s %s"
    
    fmtstr=fmtstr.replace('$c',color).replace('$n',COLOR.NORMAL)
    
    return fmtstr%(self.symbol,self.chs_name,self.last_price,self.pct_change,
                   '%',self.volume,self.pre_close, self.open,
                   self.low,self.high,self.date, self.time)