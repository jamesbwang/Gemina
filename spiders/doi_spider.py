import scrapy
import os
import re
#replace the code below with the pathway to the infections folder
dir=r"C:\Users\WJang\Desktop\Gemina_Project_Pathogens\Gemina_Project_Pathogens\infections"
newdir = os.path.join(dir, r'infections_new')
d = {}

def generatePathogenDictionary():
	global d
	for file in os.listdir(newdir):
		f = os.path.join(newdir, file)
		fileName = os.path.join(f, "pubmedAbstract.txt")
		if not f.endswith('.csv'):
			if os.path.isfile(fileName):
				PMIDfile = open(fileName, 'r')
				for url in PMIDfile:
					if url.startswith('DOI: '):
						doiUrl = 'http://doi.org/' + url[5:-2]
						d[doiUrl] = f

def getURLList():
	urlList = []
	for file in os.listdir(newdir):
		f = os.path.join(newdir, file)
		fileName = os.path.join(f, "pubmedAbstract.txt")
		if os.path.isfile(fileName):
			PMIDfile = open(fileName, 'r')
			for url in PMIDfile:
				if url.startswith('DOI: '):
					doiURL = 'http://doi.org/' + url[5:-2]
					urlList.append(doiURL)
	return urlList

class DOISpider(scrapy.Spider):
	name = "doi"
	def start_requests(self):
		generatePathogenDictionary()
		urls = getURLList()
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		url = response.request.meta['redirect_urls'][0]
		i = 0
		while os.path.join(d[url], 'DOI_' + str(i) + '.txt'):
			i+=1
		filename = os.path.join(d[url], 'DOI_' + str(i) + '.txt')
		for para in response.css('p'):
			with open(filename, 'a', encoding='utf-8') as f:
				cleanr = re.compile('<.*?>')
				cleantext = re.sub(cleanr, '', para.extract())
				f.write(cleantext)
		self.log('Saved file: ' + filename)
