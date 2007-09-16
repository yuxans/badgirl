# -*- coding: utf-8 -*-

import re
import traceback
import urllib,urllib2
import thread
import sys

from singleton import Singleton
from finance_items import FinanceItemFactory
        
class SearchEngine(Singleton):
    
    ENCODING='gbk'
    # the following url is used in http://biz.finance.sina.com.cn/suggest/lookup_n.php
    SUGGEST_URL=r'http://202.108.37.42:8086/f.suggest?q=%s'
    DATA_URL=r'http://hq.sinajs.cn/list=%s'
    SUGG_PATT=re.compile(r'everydata\[\d+\]=".*\t([a-z]+-[a-z0-9]+-.*)";', re.I)
    DATA_PATT=re.compile(r'var hq_str_.*="(.*)";', re.I)
        
    def __init__(self):
        pass
    
    def urlopen(self,url):
        req=urllib2.Request(url, None,
                            {'User-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2)'})
        return urllib2.urlopen(req)

    def fetch_content(self,url):
        handl=self.urlopen(url)
        data=handl.read().decode(SearchEngine.ENCODING)
        handl.close()
        return data
    
    def generate_suggest_url(self,qstr):
        return (SearchEngine.SUGGEST_URL%qstr).encode(SearchEngine.ENCODING)
    
    def generate_data_url(self,hqstrs):
        return SearchEngine.DATA_URL%(','.join(hqstrs))
        
    def lookup_suggests(self,qstr):
        try:
            url=self.generate_suggest_url(qstr)
            data=self.fetch_content(url)
            # suggest str is in the following format 'flag-symbol-name'
            # example: sh-600001-StockName 
            suggests=SearchEngine.SUGG_PATT.findall(data)     
        except:
            traceback.print_exc()
            suggests=[]
        return suggests
    
    def feed_all(self,items):
        succecced=[]
        try:
            num_of_items=len(items)
            if num_of_items>0:
                url=self.generate_data_url([ item.to_hqstr() for item in items ])
                rawdata=self.fetch_content(url)
                results=SearchEngine.DATA_PATT.findall(rawdata)
                if num_of_items==len(results):
                    for i in range(num_of_items):
                        if items[i].feed(results[i])==True:
                            succecced.append(items[i])
                        
        except:
            traceback.print_exc()
        
        return succecced

            
    def search(self,qstrs):
        # 1. lookup the hqstrs
        suggests=[]
        for qstr in qstrs:
            suggests+=self.lookup_suggests(qstr)
        # 2. parse the suggests into finance items(types: sh,sz,fu,ft,fx...)
        ff=FinanceItemFactory()
        items=[ ff.create(sugg) for sugg in suggests ]
        items=[ i for i in items if i != None ]
        # 3. feed all Items
        feeded_items=self.feed_all(items)
        # 4. return the finance items
        return feeded_items
    
if __name__=='__main__':
    eng=SearchEngine()
#    sugg=eng.lookup_suggests('000001')
#    for s in sugg:
#        print s.encode('gbk')
        
    items=eng.search(['600001','600050','699999'])
    for i in items:
        print ("%s"%i).encode('gbk')
    
    items=eng.search(['000001','hdgt','sfz','0981','hkd','hkyn','cu0711'])
    for i in items:
        print ("%s"%i).encode('gbk')
        