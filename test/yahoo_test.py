import feedparser,time
from datetime import datetime
from pprint import pprint
news_rss_url = "http://finance.yahoo.com/rss/headline?s=vnet"
info = feedparser.parse(news_rss_url)
#pprint(info)
print info.feed.title
#print info.feed.link
for entry in info.entries:
	print entry.title
	link = entry.link.split('*http')[1]
	print ">>> link: http" + link
	print ">>> desc: " + entry.summary
	timetuple = list(entry.published_parsed[0:8]) + [-1]
	print ">>> time: %s" % datetime.fromtimestamp(time.mktime(timetuple))
