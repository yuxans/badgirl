# -*- coding: utf-8 -*-

#####################################################################
# Meta data for sh and sz stocks
#####################################################################

from meta_map import FINANCE_META
from meta_map import COLOR

FINANCE_META['sh']={'cls':None,'attrs':None,'attr_types':None}
FINANCE_META['sz']={'cls':None,'attrs':None,'attr_types':None}

FINANCE_META['sh']['attrs']=['name','open','pre_close','last_price',
                         'high','low','bid','ask',
                         'volume','turnover','bv1','bp1',
                         'bv2','bp2','bv3','bp3',
                         'bv4','bp4','bv5','bv5',
                         'sv1','sp1','sv2','sp2',
                         'sv3','sp3','sv4','sp4',
                         'sv5','sp5','date','time']

FINANCE_META['sh']['attr_types']={'name':unicode,'pre_close':float,'open':float,'last_price':float,
                         'high':float,'low':float,'bid':float,'ask':float,
                         'volume':int,'turnover':float,'bv1':int,'bp1':float,
                         'bv2':int,'bp2':float,'bv3':int,'bp3':float,
                         'bv4':int,'bp4':float,'bv5':int,'bv5':float,
                         'sv1':int,'sp1':float,'sv2':int,'sp2':float,
                         'sv3':int,'sp3':float,'sv4':int,'sp4':float,
                         'sv5':int,'sp5':float,'date':str,'time':str}
def to_hqstr_sh(self):
    """ Example: flag='sh', symbol='600001' ==> hqstr='sh600001' """
    return self.flag+self.symbol

def to_str_sh(self):
    # cal the markup precent
    pct=0.0
    try:
        # when the market is going to open in the morning, most
        # of the data will be clear. in this situation, pct might
        # should wrong data. we need to use a simple trick to fix it
        if self.last_price >0:
            pct=100*(self.last_price-self.pre_close)/self.pre_close

    except:
        pct=0.0
    
    if pct == 0:
        color=COLOR.NORMAL
    elif pct>0:
        color=COLOR.RED
    else:
        color=COLOR.GREEN
    
    fmtstr=u"[%s] 股票名称: %s, 当前价:$c %.2f$n, 涨幅:$c %.2f%s$n, 成交量 %d, 昨收盘: %.2f, 今开盘: %.2f, 最低: %.2f, 最高: %.2f, 时 间: %s %s"
    
    fmtstr=fmtstr.replace('$c',color).replace('$n',COLOR.NORMAL)
    
    return fmtstr%(self.symbol,self.name,self.last_price,pct,
                   '%',self.volume,self.pre_close, self.open,
                   self.low,self.high,self.date, self.time)

FINANCE_META['sz']['attrs']=FINANCE_META['sh']['attrs']
FINANCE_META['sz']['attr_types']=FINANCE_META['sh']['attr_types']

def to_hqstr_sz(self):
    """ Example: flag='sz', symbol='000001' ==> hqstr='sz000001' """
    return self.flag+self.symbol

to_str_sz=to_str_sh