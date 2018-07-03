import constants
import os
import requests

def downloadPMID():
	# for every PMID.txt file, use requests to read the corresponding file and extract the relevant abstracts.
	for file in os.listdir(constants.newdir):
		if not file.endswith('.csv'):
			foldername = os.path.join(constants.newdir, file)
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


#at this point, use GeminaSpiders to download DOI papers.