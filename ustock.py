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
		self.ustock_db = self.ustock_mongo_conn['ustock_test']
		self.ustock_db.authenticate('ustock_test','chengliang')

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
		for symbol in self.ustock_db['externals'].find({'market':market},{'_id':False, 'LastSale': False, 'Sector': False, 'kind': False , 'externalid': False, 'market': False}):
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

	def get_max_articleid(self):
		id = 1
		for article in  self.ustock_db['articles'].find({},{'_id':False,'id':True}).sort([("id",pymongo.DESCENDING)]).limit(1):
			if article['id'] >= id :
				id = article['id'] + 1
		return id

	def yahoo_rss_update(self,market,symbol):
		article = dict()
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
				article['_id'] = id
				article['id'] = self.get_max_articleid()
				article['docid'] = id
				article['symbol'] = symbol
				article['sourcename'] = symbol
				article['externalid'] = symbol
				article['title'] = entry.title
				news_link = 'http' + entry.link.split('*http')[1]
				article['url'] = re.sub(re.compile("=yahoo",re.I),"=maxcl",news_link)
				article['content168'] = entry.summary
				timetuple = list(entry.published_parsed[0:8]) + [-1]
				article['date'] = int(time.mktime(timetuple))
				article['CTIME'] = 0
				article['OPENSOURCE'] = False
				article['PUBLISH'] = True
				article['SORT'] = 0
				article['TYPE'] = 'info'

				pprint(article['title'])
				#raw_input('press any key to continue')
				find_news = self.ustock_db['articles'].find_one({"_id":id})
				if not find_news:
					self.ustock_db['articles'].update({'_id':id}, article, upsert=True)
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

	def put_news_content(self,record,market):
		self.ustock_db['contents'].update({'_id':record['_id']},record,upsert=True)
		self.ustock_db['articles'].update({'_id':record['_id']},{"$set":{"CTIME":int(time.time())}})
		self.ustock_db['update_time'].update({"_id":market + '_' + record['externalid']},{"$inc":{"DocNum":1}})

	def delete_news_on_lists(self,docid):
		self.ustock_db['articles'].remove({'_id':docid})
