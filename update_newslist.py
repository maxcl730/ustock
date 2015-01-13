#!/usr/bin/python
import os,sys,time
import ustock
from pprint import pprint
market = sys.argv[1]
if market in ('amex','nasdaq','nyse'):
	ustock_obj = ustock.ustock()
	oldest_update = ustock_obj.stock_info_oldest_update(market)
	while 1 :
		if oldest_update + 86400 < time.time():
			ustock_obj.stock_info_update(market,1)
		else:
			exit(0)
else :
	print market+" is not a valid market!"