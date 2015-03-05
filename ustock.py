#!/usr/bin/python
import feedparser,pymongo,sys,copy
import time,datetime,re,hashlib
from pprint import pprint
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
		external_record = copy.deepcopy(symbol)
		external_record['externalid'] = external_record['Symbol']
		external_record['name'] = external_record['Name']
		del(external_record['Name'])
		external_record['kind'] = external_record['industry']
		del(external_record['industry'])
		del(external_record['Summary Quote'])
		external_record['TYPE'] = 0
		external_record['SORT'] = 0
		id = market + '_' + symbol['Symbol']
		self.ustock_db['externals'].remove({"_id":id})
		symbol['_id'] = id
		self.ustock_db['externals'].insert(external_record)
		print id
		if not(id.find('^') > 1 or id.find('/') > 1) :
			update_time = self.ustock_db['update_time'].find_one({"_id":id})
			if not update_time:
				self.ustock_db['update_time'].insert({"_id":id,"dotime":int(time.time())})

	def symbols_get_for_market(self,market):
		symbols = []
		for symbol in self.ustock_db['symbols'].find({'market':market},{'_id':False, 'LastSale': False, 'Summary Quote': False, 'market': False}):
			symbols.append(symbol)
		return symbols
		
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
				#self.ustock_db['articles']
				try:
					id = hashlib.md5(market + "_" + symbol + "_" + str(entry.title)).hexdigest()
				except UnicodeEncodeError:
					continue
				news['docid'] = id
				news['symbol'] = symbol
				news['sourcename'] = symbol
				news['title'] = entry.title
				news_link = 'http' + entry.link.split('*http')[1]
				news['url'] = re.sub(re.compile("=yahoo",re.I),"=maxcl",news_link)
				news['content168'] = entry.summary
				timetuple = list(entry.published_parsed[0:8]) + [-1]
				news['date'] = time.mktime(timetuple)
				news['CTIME'] = 0

				find_news = self.ustock_db['articles'].find_one({"docid":id})
				if not find_news:
					self.ustock_db['articles'].update({'docid':id},news ,upsert=True)
		except AttributeError:
			return 

	def get_news_link(self,symbol):
		news_record = []
		for new in self.ustock_db['articles'].find({'symbol':symbol,'CTIME':0},{'content168':False, 'date': False, 'sourcename': False, '_id': False}):
			#print new['link'].encode
			news_record.append(new)
		return news_record

	def get_untreated_news(self,symbol):
		news_record = []
		for new in self.ustock_db['articles'].find({'symbol':symbol,'CTIME':0},{'content168':False, 'sourcename': False, '_id': False}):
			#print new['link'].encode
			news_record.append(new)
		return news_record

	def put_news_content(self,record):
		self.ustock_db['contents'].update({'docid':record['docid']},record,upsert=True)
		self.ustock_db['articles'].update({'docid':record['docid']},{"$set":{"CTIME":int(time.time())}})
		self.ustock_db['symbols'].update({"Symbol":record['nick']},{"$inc":{"DocNum":1}})

	def delete_news_on_lists(self,docid):
		self.ustock_db['articles'].remove({'docid':docid})
