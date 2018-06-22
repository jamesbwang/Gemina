import scrapy
import os

#replace the code below with the pathway to the infections folder
dir=r"C:\Users\WJang\Desktop\Gemina_Project_Pathogens\Gemina_Project_Pathogens\infections"
newdir = os.path.join(dir, r'infections_new')
currentName = ''
d = {}

def generatePathogenDictionary():
	global d
	for file in os.listdir(newdir):
		f = os.path.join(newdir, file)
		if not f.endswith('.csv'):
			name = f[len(newdir):]
			d[name] = newdir

def getURLList():
	urlList = []
	for file in os.listdir(newdir):
		f = os.path.join(newdir, file)
		if not f.endswith('.csv') and os.path.isfile(os.path.join(f, "PMID.txt")):
			PMIDfile = open(os.path.join(f, "url.txt"), 'r')
			for url in PMIDfile:
				urlList.append(url)
	return urlList

def setName(k):
	global currentName
	currentName = k
def getName():
	return currentName

class URLSpider(scrapy.Spider):
	name = "url"
	def start_requests(self):
		generatePathogenDictionary()
		urls = getURLList()
		for url in urls:
			setName(url)
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		for abstract in response.css('div.abstr'):
			text = abstract.css('div').extract_first()
			text = text.encode('utf-8')
			filename = os.path.join(d[currentName], 'URL_')
			i = '0'
			while os.path.isfile(filename + i):
				i+=1
			filename = filename + i + '.txt'
			text = text[53:]
			text = text[:-16]
			with open(filename, 'wb') as f:
				f.write(text)
				self.log('Saved file %s' % filename)
				f.close()
