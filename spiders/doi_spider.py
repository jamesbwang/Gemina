import scrapy
import os
import scipy.spatial.distance as dist
import re
from selenium import webdriver
from scrapy.crawler import CrawlerProcess

# replace the code below with the pathway to the infections folder
dir = r"C:\Users\WJang\Desktop\Gemina_Project_Pathogens\Gemina_Project_Pathogens\infections"
newdir = os.path.join(dir, r'infections_new')
d = {}
a = []
d2 = {}
def generatePathogenDictionary():
	# generate the map that will tell the spider where to put the DOI files.
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
						if doiUrl not in d:
							d[doiUrl] = []
						d[doiUrl].append(f)


def checkReference(s, filename):
	# used to find all instances of a given reference in a PMID or DOI file
	s = s.replace('\n', ' ')
	s = s.replace('\t', ' ')
	s = s.replace('.', ' ')
	s = s.replace(',', ' ')
	s = s.replace(';', '')
	s = s.replace(':', '')
	s = s.replace('\n', ' ')
	s = s.replace('\t', ' ')
	s = s.replace('.', '')
	s = s.replace('-', ' ')
	filename = ' '.join((filename.split(' ')))
	reference = 0
	a = s.split(" ")
	for w in a:
		if (len(w) <= 3):
			continue
		if (w.endswith('es')):
			a.append(w[:-2])
		if (w.endswith('s')):
			a.append(w[:-1])
		for name in filename.split(" "):
			if (name == '.txt'):
				continue
			if (len(name) == len(w) and dist.hamming([i for i in w], [j for j in name]) * len(w) <= int(len(w) * .2)):
				reference += 1
	return reference

def getURLList():
	# generate the list of URLS to be crawled by the spider
	urlList = []
	for file in os.listdir(newdir):
		f = os.path.join(newdir, file)
		fileName = os.path.join(f, "pubmedAbstract.txt")
		if os.path.isfile(fileName):
			PMIDfile = open(fileName, 'r')
			for url in PMIDfile:
				if url.startswith('DOI: '):
					doiURL = 'http://doi.org/' + url[5:-2]
					if doiURL not in urlList:
						urlList.append(doiURL)
	return urlList


class DOISpider(scrapy.Spider):
	name = "doi2"
	def __init__(self):
		# use any browser you wish
		scrapy.Spider.__init__(self)
		self.driver = webdriver.Firefox()


	def start_requests(self):
		# map all the url-> file relationships, find all URLs, yield requests for all URLS
		generatePathogenDictionary()
		urls = a
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		# extract all paragraph tags, place the URL in the correct place.
		self.driver.implicitly_wait(60)
		self.driver.get(response.url)
		url = response.request.meta['redirect_urls'][0]
		i = 0
		for path in d2[url]:
			while os.path.isfile(os.path.join(path, 'DOI_' + str(i) + '.txt')):
				i += 1
			filename = os.path.join(path, 'DOI_' + str(i) + '.txt')
			arr = self.driver.find_elements_by_tag_name('p')
			for para in arr:
				if os.path.isfile(filename):
					with open(filename, 'a', encoding='utf-8') as f:
						f.write(para.text)
				else:
					with open(filename, 'a', encoding='utf-8') as f:
						f.write(url + '\n')
						f.write(para.text)
			self.log('Saved file: ' + filename)


class InitialSpider(scrapy.Spider):
	name = "doi"
	global d2
	global a
	def start_requests(self):
		# map all the url-> file relationships, find all URLs, yield requests for all URLS
		generatePathogenDictionary()
		urls = getURLList()
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)
		process = CrawlerProcess({})
		process.crawl(DOISpider)
		process.start() # the script will block here until the crawling is finished

	def parse(self, response):
		# extract all paragraph tags, place the URL in the correct place.
		url = response.request.meta['redirect_urls'][0]
		for path in d[url]:
			i = 0
			while os.path.isfile(os.path.join(path, 'DOI_' + str(i) + '.txt')):
				i += 1
			filename = os.path.join(path, 'DOI_' + str(i) + '.txt')
			for para in response.css('p'):
				cleanr = re.compile('<.*?>')
				cleantext = re.sub(cleanr, '', para.extract())
				with open(filename, 'a', encoding='utf-8') as f:
					f.write(cleantext)
			self.log('Saved file: ' + filename)
			s = path[len(newdir) + 1:]
			s = s.replace('_', ' ')
			s = s.replace(';', ':')
			s = s.replace('!', '?')
			s = s.replace('-', '/')
			b = False
			with open(filename, 'r', encoding = 'utf-8') as r:
				if checkReference(r.read(), s) == 0:
					b = True
					a.append(url)
					if url not in d2:
						d2[url] = []
					d2[url].append(path)
			if b:
				os.remove(filename)
				self.log('Destroyed file: ' + filename)
