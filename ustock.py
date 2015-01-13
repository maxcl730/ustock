#!/usr/bin/python
import feedparser,pymongo
import time,datetime,re,hashlib
from pprint import pprint
import sys
sys.getdefaultencoding()
reload(sys)
class ustock:
	def __init__(self):
		self.ustock_mongo_conn = pymongo.Connection('223.202.40.75', 27017)
		if not self.ustock_mongo_conn.alive():
			print "Mongodb(ustock) Connection failed"
		self.ustock_db = self.ustock_mongo_conn['ustock']
		self.ustock_db.authenticate('ustock','chengliang')

	def symbol_update(self,market,symbol):
		id = market + '_' + symbol['Symbol']
		self.ustock_db['symbols'].update({"_id":id},symbol ,upsert=True)
		print id
		if not(id.find('^') > 1 or id.find('/') > 1) :
			update_time = self.ustock_db['update_time'].find_one({"_id":id})
			if not update_time:
				self.ustock_db['update_time'].insert({"_id":id,"dotime":int(time.time())})

	def stock_info_oldest_update(self,market):
		regex = "^" + market
		oldest_update = self.ustock_db['update_time'].find_one({"$query":{"_id":re.compile(regex,re.I)},"$orderby":{"dotime":pymongo.ASCENDING}},{'_id': False})
		return oldest_update['dotime']
		
	def stock_info_update(self,market,count):
		regex = "^" + market 
		for stock in self.ustock_db['update_time'].find({"_id":re.compile(regex,re.I)}).limit(int(count)).sort([("dotime",pymongo.ASCENDING)]):
			symbol = stock['_id'].encode().split('_')[1]
			self.yahoo_rss_update(market,symbol)
			time.sleep(2)
			self.ustock_db['update_time'].update({"_id":stock['_id']},{"dotime":int(time.time())})

	def yahoo_rss_update(self,market,symbol):
		news = dict()
		print "======================" + symbol + "==================="
		news_rss_url = "http://finance.yahoo.com/rss/headline?s=" + symbol
		info = feedparser.parse(news_rss_url)
		try:
			if info.feed.title.find("feed not found") > 1 :return
			for entry in info.entries:
				#self.ustock_db['news_list']
				id = market + "_" + symbol
				try:
					id = hashlib.md5(id + entry.title).hexdigest()
				except UnicodeEncodeError:
					continue
				
				news['symbol'] = symbol
				news['title'] = entry.title
				news['link'] = 'http' + entry.link.split('*http')[1]
				news['desc'] = entry.summary
				timetuple = list(entry.published_parsed[0:8]) + [-1]
				news['time'] = time.mktime(timetuple)

				find_news = self.ustock_db['news_list'].find_one({"_id":id})
				if not find_news:
					self.ustock_db['news_list'].update({"_id":id},news ,upsert=True)
		except AttributeError:
			return 

	def get_link(self,symbol):
		news_record = []
		for new in self.ustock_db['news_list'].find({},{'desc':False, 'time': False, 'title': False}):
			#print new['link'].encode
			news_record.append(new)
		return news_record
