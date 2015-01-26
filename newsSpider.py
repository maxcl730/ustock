import urllib2,sys,re,gzip,copy
from StringIO import StringIO
#from BeautifulSoup import BeautifulSoup, Comment, Tag
from bs4 import BeautifulSoup, Comment, Tag
from pprint import pprint
sys.setdefaultencoding('utf8')
reload(sys)
class newsSpider:
	def __init__(self,url):
		self.news_url = url
		self.request =urllib2.Request(url)
		self.request.add_header('Accept-encoding','gzip')
		self.request.add_header('User-Agent','Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
		self.news_soup = BeautifulSoup()
		self.news_dict = dict()

	def get_page_to_soup(self):
		self.response = urllib2.urlopen(self.request)
		if self.response.info().get('Content-Encoding') == 'gzip':
			buf = StringIO(self.response.read())
			f = gzip.GzipFile(fileobj = buf)
			page = f.read()
		else:
			page = self.response.read()
		try:
			charset = re.search("<meta(.*)content=\"text/html(.*)charset=([a-zA-Z0-9-]+)\"",page,re.I).group(3)
		except AttributeError:
			try:
				charset = re.search("<meta charset=\"([a-zA-Z0-9-]+)\"",page,re.I).group(1)
			except AttributeError:
				charset = "utf-8"
		if re.search("(gb2312|gbk)",charset,re.I):
			page = unicode(page,charset.lower(),'ignore').encode('utf-8','ignore')
		self.news_soup = BeautifulSoup(page)

	def remove_unuseful_tag(self,content):
		#remove function tags
		extract_tags = ('style','meta','script')
		tag_items = content.findAll(extract_tags)
		[tag_item.extract() for tag_item in tag_items]
		#remove comments
		comments = content.findAll(text=lambda text:isinstance(text, Comment))
		[comment.extract() for comment in comments]
		return content

	def remove_unnecessary_tags(self,content, whitelist = ['a', 'table', 'td', 'tr', 'li' , 'br', 'ul' ,'ol', 'th']):
		#keep necessary tags
		for tag_item in content.findAll(True):
			if tag_item.name not in whitelist:
				tag_item.replaceWithChildren()
		return content

	def clean_tag_attribute(self,content, whitelist=['title','href','src']):
		content.attrs = None
		for e in content.findAll(True):
			tmp_attrs = copy.deepcopy(e.attrs)
			for attribute in tmp_attrs:
				if str(attribute) not in whitelist:
					del e[str(attribute)]
		return content

	def finance_yahoo_com(self):
		if not re.search('^http:\/\/finance.yahoo.com\/news\/',self.news_url) :
			return None
		self.get_page_to_soup()
		#keep_tags = ['a', 'table', 'td', 'tr', 'li' , 'br', 'ul' ,'ol', 'th']
		page_title = self.news_soup.find('header',attrs={"class":"header"})
		page_content = self.news_soup.find('div',attrs={"class":"body yom-art-content clearfix"})
		page_title.extract()
		page_content.extract()
		#yahoo_a_link = page_content.findAll('a', src=re.compile("\/q?s")
		#[a_tag.parent.extract() for a_tag in yahoo_a_link]

		self.news_dict['title'] = page_title.h1.string
		temp_content = self.remove_unuseful_tag(page_content)
		temp_content = self.remove_unnecessary_tags(temp_content)
		str_content = str(self.clean_tag_attribute(temp_content))
		self.news_dict['content'] = " ".join(str_content.encode('ascii',errors='ignore').split())
		return self.news_dict
