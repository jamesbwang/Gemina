import pandas as pd
import os
import extract
import constants


class Formatter:
	__dir = r''
	__newdir = ''

	def __init__(self, newDir):
		self.__dir = newDir
		self.__newdir = os.path.join(newDir, 'infections_new')

	def reformat(self):
		# edit the old Gemina database such that the columns are reformated appropriately
		# create new .csv files, print the beginnings of the new csvs, and eliminate the last col. (will use for links to the folder)
		for filename in os.listdir(self.__dir):
			if filename.endswith(".csv"):
				df = pd.read_table(os.path.join(self.__dir, filename), sep="\t", comment="#",
								   names=['index', 'pathogen', 'source', 'disease', 'tsource', 'ttype', 'portal',
										  'infection_atts', 'tatts', 'comments']).reset_index()
				# add all the abstracts of the paper(or html for now)
				self.__addAbstract(df, filename)
				continue
			else:
				continue
		self.__appendSuffixes()
		extract.downloadPMID()

	def __appendSuffixes(self):
		# to all the pubmed links, append the correct suffix so that requests can successfully process the text and that the url listed is valid
		for folder in os.listdir(self.__newdir):
			PMIDpath = os.path.join(os.path.join(self.__newdir, folder), 'PMID.txt')
			if (os.path.isfile(PMIDpath)):
				with open(PMIDpath, 'r') as valid:
					if '&retmode=text&rettype=abstract%0A' in valid.read():
						print('fail')
						valid.close()
						continue
				with open(PMIDpath, 'rb+') as filehandle:
					filehandle.seek(-1, os.SEEK_END)
					filehandle.truncate()
					filehandle.close()
				with open(PMIDpath, 'a', encoding='utf-8') as filename:
					filename.write("&retmode=text&rettype=abstract%0A")
					print("adding suffixes to pubmed links....")
					filename.close()

	def __addAbstract(self, file, fileName):
		# for the column infection_tatts, separate the urls and the PMID's: we will treat these two cases separately.
		k = 0
		for v in file['infection_atts']:
			# find the name in the corresponding pathogen column

			# create the name we'll use in the directory
			dirname = str(file.iloc[k, 2])
			dirname = dirname.replace(' ', '_').replace(':', ';').replace('?', '!').replace('/', '-')

			# create the path we'll put the files in, separated by pathogen
			path = os.path.join(self.__newdir, dirname)
			print(path)
			if not os.path.exists(path):
				os.makedirs(path)

			# insert the directory into the dataframe
			file.at[k, 'links'] = path
			disease = file.at[k, 'disease']
			if isinstance(disease, str):
				with open(os.path.join(path, 'disease.txt'), 'w', encoding='utf-8') as f:
					f.write(disease)
			k += 1
			# break down the PMID/URL's, address them accordingly
			if isinstance(v, str):
				self.__addAbstractHelper(v, path)
		# create the file we'll insert into the new_infection database
		filepath = os.path.join(self.__newdir, 'new' + fileName)
		print(filepath)
		# convert the dataframe to csv format
		file.to_csv(filepath)

	def __addAbstractHelper(self, v, path):
		if len(v) == 0:
			return

		# address every entry, and store PMIDs, toxins, symptoms, and relevant URLS in the same place.
		while len(v) > 0:
			if v.startswith('URL:'):
				# create the URL file
				v = v[4:]
				count = 0
				while count < len(v) and v[count] != ';':
					count += 1
				j = v[: count]
				v = v[count:]
				newpath = os.path.join(path, 'url.txt')
				with open(newpath, 'a', encoding='utf-8') as file:
					file.write(j + '\n')
					file.close()
				continue
			if v.startswith('PMID:'):
				# create the PMID file
				v = v[5:]
				count = 0
				while count < len(v) and v[count] != ';':
					count += 1
				j = v[: count]
				v = v[count:]
				newpath = os.path.join(path, 'PMID.txt')
				if os.path.isfile(newpath):
					with open(newpath, 'r', encoding='utf-8') as valid:
						if j in valid.read():
							continue
						with open(newpath, 'a', encoding='utf-8') as file:
							file.write(j + ',')
							file.close()
				else:
					with open(newpath, 'w', encoding='utf-8') as file:
						file.write('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=' + j + ',')
						file.close()
				continue
			if v.startswith("toxin="):
				v = v[6:]
				count = 0
				while count < len(v) and v[count] != ';':
					count += 1
				j = v[: count]
				v = v[count:]
				# print('\t' + j)
				newpath = os.path.join(path, "toxins.txt")
				# print(newpath)
				if os.path.isfile(newpath):
					file = open(newpath, "r")
					if j in file.read():
						continue
					file = open(newpath, 'a')
				else:
					file = open(newpath, "w+")
				file.write(j + " ")
				file.close()
				continue
			if v.startswith("symptom="):
				v = v[8:]
				count = 0
				while count < len(v) and v[count] != ';':
					count += 1
				j = v[: count]
				v = v[count:]
				newpath = os.path.join(path, "symptoms.txt")
				if os.path.isfile(newpath):
					file = open(newpath, "r")
					if j in file.read():
						continue
					file = open(newpath, 'a')
				else:
					file = open(newpath, "w+")
				file.write(j + ", ")
				file.close()
				continue
			else:
				v = v[1:]
				continue

	def combineNewCSV(self):
		# combine all reformatted Gemina CSVs to the same file, preparing for tagging
		df = pd.DataFrame()
		for file in os.listdir(self.__newdir):
			if file.endswith('.csv') and file.startswith('new'):
				print(file)
				if df.empty:
					df = pd.read_csv(os.path.join(self.__newdir, file), index_col=0).drop('index', axis=1).set_index(
						'pathogen')
					df = df.sort_index()
				else:
					df = df.append(
						pd.read_csv(os.path.join(self.__newdir, file), index_col=0).drop('index', axis=1).drop(
							0).set_index('pathogen'), sort=True)
		print('successfully joined all Gemina files')
		df = df.drop('level_0', axis=1)
		df.to_csv(constants.COMBINED_CSV)

	def createUniqueCSV(self):
		df = pd.read_csv('full_ontology.csv').sort_values(by=['pathogen'])
		newdf = pd.DataFrame(
			columns=['pathogen', 'comments', 'disease', 'infection_atts', 'links,portal', 'source', 'tatts', 'tsource',
					 'ttype', 'symptoms'])
		for index, row in df.iterrows():
			if newdf.shape[0] - 1 < 0 or row['pathogen'] != newdf.loc[newdf.shape[0] - 1, 'pathogen']:
				newdf.loc[newdf.shape[0]] = row.append(pd.Series(''))
			else:
				for word in str(newdf.loc[newdf.shape[0] - 1]['disease']).replace(';', ',').split(','):
					if word.replace(' ', '') not in str(newdf.loc[newdf.shape[0] - 1]['disease']).replace(' ',
																										  '').replace(
							';', ',').split(','):
						newdf.loc[newdf.shape[0] - 1]['disease'] = str(newdf.loc[newdf.shape[0] - 1]['disease']) + (
									';' + word)
			if os.path.isfile(os.path.join(row['links'], 'symptoms.txt')):
				with open(os.path.join(row['links'], 'symptoms.txt'), 'r', encoding='utf-8') as f:
					for word in f.read().split(','):
						if word.replace(' ', '') not in str(newdf.loc[newdf.shape[0] - 1]['symptoms']).replace(' ',
																											   '').split(
								',') and word != 'nan':
							newdf.loc[newdf.shape[0] - 1]['symptoms'] = str(
								newdf.loc[newdf.shape[0] - 1]['symptoms']) + ' ' + word + ','
		newdf.to_csv(constants.UNIQUE_ONTOLOGY)
