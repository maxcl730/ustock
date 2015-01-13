try:
	#Using bs4
	from bs4 import BeautifulStoneSoup
	from bs4 import Tag
except ImportError:
	#Using bs3
	from BeautifulSoup import BeautifulStoneSoup
	from BeautifulSoup import Tag

def info_extract(isoup):
	'''
	Recursively walk a nested list and upon finding a non iterable, return its string
	'''
	tlist = []
	def info_extract_helper(inlist, count = 0):
		if(isinstance(inlist, list)):
			for q in inlist:
				if(isinstance(q, Tag)):
					info_extract_helper(q.contents, count + 1)
				else:
					extracted_str = q.strip()
					if(extracted_str and (count > 1)):
						tlist.append(extracted_str)
	info_extract_helper([isoup])
	return tlist

xml_str = \
'''
<?xml version="1.0" encoding="UTF-8"?>
    <first-tag>
      <second-tag>
        <events-data>
           <event-date someattrib="test">
                <date>20040913</date>
           </event-date>
        </events-data>

      <events-data>
         <event-date>
           <date>20040913</date>
         </event-date>
      </events-data> 
     </second-tag>
   </first-tag>
'''

soup = BeautifulStoneSoup(xml_str)
print info_extract(soup)
