import urllib2,sys,re,gzip
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup
from pprint import pprint

url = sys.argv[1]

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
request = urllib2.Request(url)
request.add_header('Accept-encoding','gzip')
request.add_header('User-Agent',user_agent)

response = urllib2.urlopen(request)
if response.info().get('Content-Encoding') == 'gzip':
	buf = StringIO(response.read())
	f = gzip.GzipFile(fileobj=buf)
	page = f.read()
else:
	page = response.read()
try:
	charset = re.search("<meta(.*)content=\"text/html; charset=([a-zA-Z0-9-]+)\"",page,re.I).group(2)
except AttributeError:
	try :
		charset = re.search("<meta charset=\"([a-zA-Z0-9-]+)\"",page,re.I).group(1)
	except AttributeError:
		print "error"
		charset = "UTF-8"
print charset
exit(0)
if re.search("(gb2312|gbk)",charset,re.I) :
	page = unicode(page,charset.lower(),'ignore').encode('utf-8','ignore')
soup = BeautifulSoup(page)

#print soup.prettify()
#print "=========================================================="
texts = soup.findAll(text=True)
def visible_text(element):
	if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
		return ''
	result = re.sub('<!--.*-->', '', str(element), flags=re.DOTALL)
	#result = re.sub('<!--.*-->|\r|\n', '', str(element), flags=re.DOTALL)
	result = re.sub('\s{2,}|&nbsp;', ' ', result)
	return result

visible_elements = [visible_text(elem) for elem in texts]
visible_text = ''.join(visible_elements)
print(visible_text)
