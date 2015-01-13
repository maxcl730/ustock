#!/usr/bin/python
import os,sys,urlparse
import ustock
from pprint import pprint
'''
market = sys.argv[1]
if market in ('amex','nasdaq','nyse'):
	ustock_obj = ustock.ustock()
	ustock_obj.stock_info_update(market,1)
else :
	print market+" is not a valid market!"
'''
ustock_obj = ustock.ustock()
host_count = dict()
for new in ustock_obj.get_link('OK'):
	parsedTuple = urlparse.urlparse(new['link'].encode())
	if not (parsedTuple.netloc in host_count):
		host_count[parsedTuple.netloc] = 1
	else:
		host_count[parsedTuple.netloc] = host_count[parsedTuple.netloc] + 1
print sorted(host_count.items(), key=lambda d: d[1]) 
#pprint(host_count)
