#!/usr/bin/python
import os,sys
import ustock
from pprint import pprint
symbol_object = list()
symbol = dict()
filename = sys.argv[1]
if not(os.path.exists(filename)) or not(filename.endswith(".csv")):
	print "Error load symbols file!"
	exit(1)
market = os.path.basename(filename).split('-')[0]
print "Market:" + market
symbols = open(filename)
ustock_obj = ustock.ustock()
while True:
	records = symbols.readlines(1000)
	if not records: break
	for record in records:
		try:
			record = record.rstrip()
			record = record.rstrip(',')
			record = record.strip('"')
			if record.split(',')[0].find('Symbol') >= 0:
				for element in record.split(','):
					symbol_object.append(element.replace('"',''))
			else:
				count = 0
				for object in symbol_object :
					symbol[object] = record.split('","')[count].strip()
					count = count + 1
				symbol['market'] = market
				ustock_obj.symbol_update(market,symbol)
		except ValueError:
			continue
