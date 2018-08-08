import constants
import os
import requests
import json


def downloadPMID():
	# for every PMID.txt file, use requests to read the corresponding file and extract the relevant abstracts.
	for file in os.listdir(constants.NEW_DIR):
		if not file.endswith('.csv'):
			foldername = os.path.join(constants.NEW_DIR, file)
			pathname = os.path.join(foldername, 'PMID.txt')
			print(pathname)
			if os.path.isfile(pathname):
				with open(pathname, 'r', encoding='utf-8') as f:
					try:
						r = requests.get(f.read())
						with open(os.path.join(foldername, 'pubmedAbstract.txt'), 'w+', encoding='utf-8') as newfile:
							newfile.write(r.text)
							print('success')
					except:
						print('failure')
						continue
			else:
				print('path does not exist')


# download all PMID records in XML format from the pubMed database
class PubMedFetcher:
	__search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&mindate=1800/01/01&maxdate=2018/06/29&usehistory=y&retmode=json"
	__search_r = requests.post(__search_url)
	__search_data = __search_r.json()
	__webenv = __search_data["esearchresult"]['webenv']
	__total_records = int(__search_data["esearchresult"]['count'])
	__fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=xml&retmax=9999&query_key=1&webenv=" + __webenv

	def fetchAbstracts(self):
		for i in range(0, self.__total_records, 10000):
			this_fetch = self.__fetch_url + "&retstart=" + str(i)
			print("Getting this URL: " + this_fetch)
			fetch_r = requests.post(this_fetch)
			f = open('pubmed_batch_' + str(i) + '_to_' + str(i + 9999) + ".xml", 'w', encoding='utf-8')
			f.write(fetch_r.text)
			f.close()
		print("Number of records found :" + str(self.__total_records))

# at this point, use GeminaSpiders to download DOI papers.
