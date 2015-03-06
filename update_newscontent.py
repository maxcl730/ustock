#!/usr/bin/python
import os,sys,re,urlparse,signal,hashlib,time
import ustock,newsSpider
from pprint import pprint

def myhandle(signalNun, currentStackFrame):
	print "%s exit(%d)." %(sys.argv[0],signalNun)
	sys.exit(0)

signal.signal(signal.SIGINT,myhandle)
reload(sys)
sys.setdefaultencoding('utf8')

market = sys.argv[1]
if not (market in ('amex','nasdaq','nyse')):
	print market+" is not a valid market!"
	exit(1)

#ustock_obj.stock_info_update(market,1)
'''
#Test symbos
Symbols = ('CRESY','JRJC','YY','BABA')
'''

ustock_obj = ustock.ustock()
stocks = ustock_obj.symbols_get_for_market(market)
for stock in stocks:
	Symbol = stock['Symbol']
	print ("=======%s_%s: news list=======") % (market,Symbol)
	for news in ustock_obj.get_untreated_news(Symbol):
		parsedTuple = urlparse.urlparse(news['url'].encode())
		#test special host
		#if not re.search('^http:\/\/www.noodls.com\/view\/',news['url']) :
		#	continue
		pprint(news)
		hostname_func = re.sub('\.','_',parsedTuple.netloc)
		spider = newsSpider.newsSpider(news['url'])
		if hasattr(spider,hostname_func):
			hostname_func = 'spider.'+hostname_func+'()'
			article = eval(hostname_func)
			if article is None:
				continue
			article['ARTICLES'] = news['id']
			article['id'] = news['id']
			article['docid'] = hashlib.md5(market + "_" + Symbol + "_" + str(news['title'])).hexdigest()
			article['_id'] = article['docid']
			if article['code'] == 404 :
				ustock_obj.delete_news_on_lists(article['_id'])
				continue
			article['date'] = news['date']
			article['externalid'] = Symbol
			article['nick'] = Symbol
			article['url'] = news['url']
			article['CTIME'] = int(time.time())
			
			pprint(article)
			raw_input('press any key to continue')
			ustock_obj.put_news_content(article,market)
