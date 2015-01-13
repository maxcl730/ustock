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
host = set()
for new in ustock_obj.get_link('OK'):
	parsedTuple = urlparse.urlparse(new['link'].encode())
	host.add(parsedTuple.netloc)
for n in host:
	print n
