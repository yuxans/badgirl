# -*- coding: utf-8 -*-

#####################################################################
# Meta data for futures market
#####################################################################

from meta_map import FINANCE_META
from meta_map import COLOR

FINANCE_META['ft']={'cls':None,'attrs':None,'attr_types':None}

FINANCE_META['ft']['attrs']=['name','time','open','high',
                         'low','unkown','bid','ask',
                         'last_price','dsp','ysp','buy_volume',
                         'sell_volume','position','turnover','exchage',
                         'category']
FINANCE_META['ft']['attr_types']={'name':unicode,'time':str,'open':float,'high':float,
                         'low':float,'unkown':float,'bid':float,'ask':float,
                         'last_price':float,'dsp':float,'ysp':float,'buy_volume':int,
                         'sell_volume':int,'position':float,'turnover':float,'exchage':unicode,
                         'category':unicode}

def to_hqstr_ft(self):
    """ 
        Sina is stupid. the hqstr formats for the ft stuffs are not unified.
        Some tricks are needed here...
    """
    prefix=self.symbol[:2]
    UPPER_NEEDED=('wt','ws','cf','sr','ta','ro')
    return (prefix in UPPER_NEEDED) and self.symbol.upper() or self.symbol

def to_str_ft(self):
    
    timestr=self.time
    if len(timestr)==6:
        timestr="%s:%s:%s"%(timestr[:2],timestr[2:4],timestr[4:])
    else:
        timestr="--:--:--"
    
    try:
        pct=100*(self.last_price-self.ysp)/self.ysp
    except:
        pct=0.0
        
    
    if pct ==0:
        color=COLOR.NORMAL
    elif pct>0:
        color=COLOR.RED
    else:
        color=COLOR.GREEN
    
    fmtstr=u"[%s] 名称: %s, 当前价:$c %.0f$n, 涨幅:$c %.2f%s$n, 开盘: %.0f, 最高: %.0f, 最低: %.0f, 买价: %.0f, 卖价 %.0f, 动态结算: %.0f, 昨结算: %.0f, 买量 %d, 卖量 %d, 持仓量: %.0f, 成交量 %.0f, 时间: %s"
    
    fmtstr=fmtstr.replace('$c',color).replace('$n',COLOR.NORMAL)
    
    return fmtstr%(self.symbol,self.name,self.last_price,pct,
                   '%',self.open,self.high, self.low,
                   self.bid,self.ask,self.dsp, self.ysp,
                   self.buy_volume,self.sell_volume,self.position,self.turnover,
                   timestr)