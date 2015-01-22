#!/usr/bin/python
import os,sys,re,urlparse
import ustock,newsSpider
from pprint import pprint
market = sys.argv[1]
if not (market in ('amex','nasdaq','nyse')):
	print market+" is not a valid market!"
	exit(1)

#ustock_obj.stock_info_update(market,1)
Symbols = ('CRESY','JRJC','YY','BABA')
ustock_obj = ustock.ustock()
#stocks = ustock_obj.symbols_get_for_market(market)
#for stock in stocks:
for Symbol in Symbols:
	#Symbol = stock['Symbol']
	print ("=======%s: news list=======") % Symbol
	for news in ustock_obj.get_news_link(Symbol):
		parsedTuple = urlparse.urlparse(news['url'].encode())
		if re.search('^http:\/\/finance.yahoo.com\/news\/',news['url']):
			pprint(news)
			hostname_func = re.sub('\.','_',parsedTuple.netloc)
			spider = newsSpider.newsSpider(news['url'])
			spider.get_page_to_soup()
			article = spider.finance_yahoo_com()
			hostname_func = re.sub('\.','_',parsedTuple.netloc)
			pprint(article)
