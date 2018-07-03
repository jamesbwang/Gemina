import constants
import pandas as pd
import os
import requests
import scipy.spatial.distance as dist

from pycorenlp import StanfordCoreNLP


def reformat():
	# edit the old Gemina database such that the columns are reformated appropriately
	# create new .csv files, print the beginnings of the new csvs, and eliminate the last col. (will use for links to the folder)
	for filename in os.listdir(constants.dir):
		if filename.endswith(".csv"):
			df = pd.read_table(os.path.join(constants.dir, filename), sep="\t", comment="#",
							   names=['index', 'pathogen', 'source', 'disease', 'tsource', 'ttype', 'portal',
									  'infection_atts', 'tatts', 'comments'])
			df.reset_index()
			# add all the abstracts of the paper(or html for now)
			addAbstract(df, filename)
			continue
		else:
			continue


def appendSuffixes():
	# to all the pubmed links, append the correct suffix so that requests can successfully process the text and that the url listed is valid
	for folder in os.listdir(constants.newdir):
		PMIDpath = os.path.join(os.path.join(constants.newdir, folder), 'PMID.txt')
		if (os.path.isfile(PMIDpath)):
			with open(PMIDpath, 'r') as valid:
				if valid.read().__contains__('&retmode=text&rettype=abstract%0A'):
					valid.close()
					return
			with open(PMIDpath, 'rb+') as filehandle:
				filehandle.seek(-1, os.SEEK_END)
				filehandle.truncate()
				filehandle.close()
			with open(PMIDpath, 'a', encoding='utf-8') as filename:
				filename.write("&retmode=text&rettype=abstract%0A")
				print("adding suffixes to pubmed links....")
				filename.close()


def addAbstract(file, fileName):
	# for the column infection_tatts, separate the urls and the PMID's: we will treat these two cases separately.
	k = 0
	for v in file['infection_atts']:
		# find the name in the corresponding pathogen column

		# create the name we'll use in the directory
		dirname = file.iloc[k, 1]
		dirname = dirname.replace(' ', '_')
		dirname = dirname.replace(':', ';')
		dirname = dirname.replace('?', '!')
		dirname = dirname.replace('/', '-')

		# create the path we'll put the files in, separated by pathogen
		path = os.path.join(constants.newdir, dirname)
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
			addAbstractHelper(v, path)

	# create the file we'll insert into the new_infection database
	filepath = os.path.join(constants.newdir, 'new' + fileName)
	print(filepath)
	# convert the dataframe to csv format
	file.to_csv(filepath)


def addAbstractHelper(v, path):
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
			file.write(j + " ")
			file.close()
			continue
		else:
			v = v[1:]
			continue


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


def unique_list(l):
	# used to make a string with no repeating words
	ulist = []
	[ulist.append(x) for x in l if x not in ulist]
	return ulist


sympCount = 0
toxCount = 0
sympReference = 0
toxReference = 0
diseaseCount = 0
disReference = 0

def checkReference(s, filename, i, path, col1 = [], col2 = [], col3 = [], col4 = [], col5 = []):
	nlp = StanfordCoreNLP('http://localhost:9000')
	# used to find all instances of a given reference in a PMID or DOI file
	sympPath = os.path.join(path, 'symptoms.txt')
	toxPath = os.path.join(path, 'toxins.txt')
	disPath = os.path.join(path, 'disease.txt')
	symp = ''
	tox = ''
	dis = ''
	global sympCount
	global toxCount
	global sympReference
	global toxReference
	global diseaseCount
	global disReference
	if os.path.isfile(sympPath):
		sympFile = open(sympPath, 'r')
		sympCount += 1
		symp = sympFile.read().lower()

	if os.path.isfile(toxPath):
		toxFile = open(toxPath, 'r')
		tox = toxFile.read().lower()
		toxCount += 1

	if os.path.isfile(disPath):
		disFile = open(disPath, 'r')
		dis = disFile.read().lower()
		diseaseCount += 1

	s = s.replace('\n', ' ')
	s = s.replace('\t', ' ')
	s = s.replace('-', ' ')
	output = nlp.annotate(s, properties={
		'annotators': 'pos',
		'outputFormat': 'json'
	})
	filename = ' '.join(unique_list(filename.split(' ')))
	symp = ' '.join(unique_list(symp.split(' ')))
	tox = ' '.join(unique_list(tox.split(' ')))
	dis = ' '.join(unique_list(dis.split(' ')))

	reference = 0
	symptomReference = 0
	toxinReference = 0
	diseaseReference = 0

	a = []
	for sentence in output["sentences"]:
		for t in sentence["tokens"]:
			if t["pos"].find("NN") != -1 or t["pos"].find("JJ") != -1 or t["pos"].find("RB") != -1 or t["pos"].find("VB") != -1:
				a.append(t["word"])
	for w in a:
		if (len(w) <= 3):
			continue
		if (w.endswith('es')):
			a.append(w[:-2])
		if (w.endswith('s')):
			a.append(w[:-1])
		for name in filename.split(" "):
			if name == '.txt':
				continue
			if (len(name) == len(w) and dist.hamming([i for i in w], [j for j in name]) * len(w) <= int(len(w) * .2)):
				reference += 1
		for symptom in symp.split(" "):
			if (len(symptom) == len(w) and dist.hamming([i for i in w], [j for j in symptom]) * len(w) <= int(
					len(w) * .2)):
				symptomReference += 1
		for toxin in tox.split(" "):
			if (len(toxin) == len(w) and dist.hamming([i for i in w], [j for j in toxin]) * len(w) <= int(
					len(w) * .2) and toxin not in filename):
				toxinReference += 1
		for disease in dis.split(" "):
			if (len(disease) == len(w) and dist.hamming([i for i in w], [j for j in disease]) * len(w) <= int(
					len(w) * .2) and disease not in filename):
				diseaseReference += 1

	print(filename + ' reference No. ' + str(i) + ':    ' + str(reference))
	print('\t' + 'symptom references: ' + (str(-1) if symp == '' else str(symptomReference)))
	print('\t' + 'toxin references: ' + (str(-1) if tox == '' else str(toxinReference)))
	print('\t' + 'disease references: ' + (str(-1) if dis == '' else str(diseaseReference)))

	col1.append(filename + ' no.: ' + str(i))
	col2.append(reference)
	if (symp != ''):
		col3.append(symptomReference)
	else:
		col3.append(-1)
	if tox != '':
		col4.append(toxinReference)
	else:
		col4.append(-1)
	if dis != '':
		col5.append(diseaseReference)
	else:
		col5.append(-1)
	sympReference += symptomReference
	toxReference += toxinReference
	disReference += diseaseReference
	return reference


def finishedStatsDOI():
	# used to find all the references of symptoms, toxins, and names for all DOI files
	global sympCount
	global toxCount
	global sympReference
	global toxReference
	global diseaseCount
	sympCount = 0
	toxCount = 0
	sympReference = 0
	toxReference = 0
	diseaseCount = 0

	numDOI = 0
	referenceTotal = 0
	col1 = []
	col2 = []
	col3 = []
	col4 = []
	coldisease = []
	for file in os.listdir(constants.newdir):
		filename = file.replace('_', ' ')
		filename = filename.replace(';', ':')
		filename = filename.replace('!', '?')
		filename = filename.replace('-', '/')
		if not file.endswith('.csv'):
			for innerFile in os.listdir(os.path.join(constants.newdir, file)):
				if innerFile.startswith('DOI'):
					i = int(innerFile[4:5])
					if i == 1 and innerFile[5].isdigit():
						i = 10 * i + int(innerFile[5])
					numDOI += 1
					f = open(os.path.join(constants.newdir, file, innerFile), 'r', encoding='utf-8')
					s = f.read().lower()
					j = checkReference(s, filename.lower(), i, os.path.join(constants.newdir, file), col1, col2, col3, col4, coldisease)
					referenceTotal += j
	print(
		"On average, names are listed below the hamming threshold " + str(referenceTotal / numDOI) + ' times per DOI.')
	print("On average, diseases are listed below the hamming threshold " + str(disReference/diseaseCount) + ' times per DOI')

	print("On average, if symptoms are available, they are listed below the hamming threshold  " + str(
		sympReference / sympCount) + ' times per DOI.')
	print('On average, if toxins are available, they are listed below the hamming threshold ' + str(
		toxReference / toxCount) + ' times per DOI.')
	finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	finishedStats['Pathogen'] = col1
	finishedStats['Name References'] = col2
	finishedStats['Symptom References'] = col3
	finishedStats['Toxin References'] = col4
	finishedStats['Disease References'] = coldisease
	finishedStats.set_index('Pathogen', inplace=True)
	finishedStats.to_csv(os.path.join(constants.newdir, 'abstractReviewDOI.csv'))

	finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	i = 0
	col5 = []
	col6 = []
	col7 = []
	col8 = []
	col9 = []
	while i < len(col1):
		if col2[i] > 0 and coldisease[i] > 0 and col3[i] > 0 and col4[i] > 0:
			col5.append(col1[i])
			col6.append(col2[i])
			col7.append(col3[i])
			col8.append(col4[i])
			col9.append(coldisease[i])
		i += 1
	finishedStats['Pathogen'] = col5
	finishedStats['Name References'] = col6
	finishedStats['Symptom References'] = col7
	finishedStats['Toxin References'] = col8
	finishedStats['Disease References'] = col9
	finishedStats.set_index('Pathogen', inplace=True)

	finishedStats.to_csv(os.path.join(constants.newdir, 'allExistDOI.csv'))

	finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	i = 0
	col5 = []
	col6 = []
	col7 = []
	col8 = []
	col9 = []
	while i < len(col1):
		if col2[i] > 0 and coldisease[i] > 0 and col3[i] > 0 and col4[i] == -1:
			col5.append(col1[i])
			col6.append(col2[i])
			col7.append(col3[i])
			col8.append(col4[i])
			col9.append(coldisease[i])
		i += 1
	finishedStats['Pathogen'] = col5
	finishedStats['Name References'] = col6
	finishedStats['Symptom References'] = col7
	finishedStats['Toxin References'] = col8
	finishedStats['Disease References'] = col9
	finishedStats.set_index('Pathogen', inplace=True)

	finishedStats.to_csv(os.path.join(constants.newdir, 'SymptomsExistDOI.csv'))
	finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	i = 0
	col5 = []
	col6 = []
	col7 = []
	col8 = []
	col9 = []
	while i < len(col1):
		if col2[i] > 0 and col3[i] == -1 and col4[i] == -1:
			col5.append(col1[i])
			col6.append(col2[i])
			col7.append(col3[i])
			col8.append(col4[i])
			col9.append(coldisease[i])
		i += 1
	finishedStats['Pathogen'] = col5
	finishedStats['Name References'] = col6
	finishedStats['Symptom References'] = col7
	finishedStats['Toxin References'] = col8
	finishedStats['Disease References'] = col9
	finishedStats.set_index('Pathogen', inplace=True)

	finishedStats.to_csv(os.path.join(constants.newdir, 'OnlyNameDOI.csv'))
	finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	i = 0
	col5 = []
	col6 = []
	col7 = []
	col8 = []
	col9 = []
	while i < len(col1):
		if col2[i] > 0 or col3[i] > 0 - 1 or col4[i] > 0 or coldisease[i] > 0:
			col5.append(col1[i])
			col6.append(col2[i])
			col7.append(col3[i])
			col8.append(col4[i])
			col9.append(coldisease[i])
		i += 1
	finishedStats['Pathogen'] = col5
	finishedStats['Name References'] = col6
	finishedStats['Symptom References'] = col7
	finishedStats['Toxin References'] = col8
	finishedStats['Disease References'] = col9
	finishedStats.set_index('Pathogen', inplace=True)

	finishedStats.to_csv(os.path.join(constants.newdir, 'AtLeastItsSomethingDOI.csv'))


def finishedStatsAbstracts():
	# used to find all the references of symptoms, toxins, and names for all abstracts
	global sympCount
	global toxCount
	global sympReference
	global toxReference
	global diseaseCount
	sympCount = 0
	toxCount = 0
	sympReference = 0
	toxReference = 0
	diseaseCount = 0

	numPathogens = 0
	numDOI = 0
	numPMID = 0
	referenceTotal = 0
	col1 = []
	col2 = []
	col3 = []
	col4 = []
	coldisease = []
	for file in os.listdir(constants.newdir):
		filename = file.replace('_', ' ')
		filename = filename.replace(';', ':')
		filename = filename.replace('!', '?')
		filename = filename.replace('-', '/')
		if not file.endswith('.csv'):
			numPathogens += 1
			for innerFile in os.listdir(os.path.join(constants.newdir, file)):
				if innerFile.startswith('DOI'):
					numDOI += 1
				elif (innerFile.startswith('pubmed')):
					f = open(os.path.join(os.path.join(constants.newdir, file), 'pubmedAbstract.txt'), 'r',
							 encoding='utf-8')
					i = 1
					s = ""
					for line in f:
						if (line.startswith(str(i) + '. ')):
							numPMID += 1
						if (line.startswith('PMID')):
							j = checkReference(s.lower(), filename.lower(), i, os.path.join(constants.newdir, file), col1, col2, col3, col4, coldisease)
							referenceTotal += j
							i += 1
							s = ''
						else:
							s += line
	print("Pathogens: " + str(numPathogens))
	print("DOI: " + str(numDOI))
	print("Abstracts: " + str(numPMID))
	print("On average, names are listed below the hamming threshold " + str(
		referenceTotal / numPMID) + ' times per abstract')
	print("On average, disease are listed below the hamming threshold " + str(disReference/diseaseCount) + ' times per abstract')
	print("On average, if symptoms are available, they are listed below the hamming threshold  " + str(
		sympReference / sympCount) + ' times per abstract.')
	print('On average, if toxins are available, they are listed below the hamming threshold ' + str(
		toxReference / toxCount) + ' times per abstract.')

	finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	finishedStats['Pathogen'] = col1
	finishedStats['Name References'] = col2
	finishedStats['Symptom References'] = col3
	finishedStats['Toxin References'] = col4
	finishedStats['Disease References'] = coldisease
	finishedStats.set_index('Pathogen', inplace=True)
	finishedStats.to_csv(os.path.join(constants.newdir, 'abstractReview.csv'))

	finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	i = 0
	col5 = []
	col6 = []
	col7 = []
	col8 = []
	col9 = []
	while i < len(col1):
		if col2[i] > 0 and coldisease[i] > 0 and col3[i] > 0 and col4[i] > 0:
			col5.append(col1[i])
			col6.append(col2[i])
			col7.append(col3[i])
			col8.append(col4[i])
			col9.append(coldisease[i])
		i += 1
	finishedStats['Pathogen'] = col5
	finishedStats['Name References'] = col6
	finishedStats['Symptom References'] = col7
	finishedStats['Toxin References'] = col8
	finishedStats['Disease References'] = col9
	finishedStats.set_index('Pathogen', inplace=True)

	finishedStats.to_csv(os.path.join(constants.newdir, 'allExist.csv'))

	finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	i = 0
	col5 = []
	col6 = []
	col7 = []
	col8 = []
	col9 = []
	while i < len(col1):
		if col2[i] > 0 and coldisease[i] > 0 and col3[i] > 0 and col4[i] == -1:
			col5.append(col1[i])
			col6.append(col2[i])
			col7.append(col3[i])
			col8.append(col4[i])
			col9.append(coldisease[i])
		i += 1
	finishedStats['Pathogen'] = col5
	finishedStats['Name References'] = col6
	finishedStats['Symptom References'] = col7
	finishedStats['Toxin References'] = col8
	finishedStats['Disease References'] = col9
	finishedStats.set_index('Pathogen', inplace=True)

	finishedStats.to_csv(os.path.join(constants.newdir, 'SymptomsExist.csv'))

	finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	i = 0
	col5 = []
	col6 = []
	col7 = []
	col8 = []
	col9 = []
	while i < len(col1):
		if col2[i] > 0 and coldisease[i] > 0 and col3[i] == -1 and col4[i] == -1:
			col5.append(col1[i])
			col6.append(col2[i])
			col7.append(col3[i])
			col8.append(col4[i])
			col9.append(coldisease[i])
		i += 1
	finishedStats['Pathogen'] = col5
	finishedStats['Name References'] = col6
	finishedStats['Symptom References'] = col7
	finishedStats['Toxin References'] = col8
	finishedStats['Disease References'] = col9
	finishedStats.set_index('Pathogen', inplace=True)

	finishedStats.to_csv(os.path.join(constants.newdir, 'OnlyName.csv'))

	finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	i = 0
	col5 = []
	col6 = []
	col7 = []
	col8 = []
	col9 = []
	while i < len(col1):
		if col2[i] > 0 or col3[i] > 0 - 1 or col4[i] > 0 or coldisease[i] > 0:
			col5.append(col1[i])
			col6.append(col2[i])
			col7.append(col3[i])
			col8.append(col4[i])
			col9.append(coldisease[i])
		i += 1
	finishedStats['Pathogen'] = col5
	finishedStats['Name References'] = col6
	finishedStats['Symptom References'] = col7
	finishedStats['Toxin References'] = col8
	finishedStats['Disease References'] = col9
	finishedStats.set_index('Pathogen', inplace=True)
	finishedStats.to_csv(os.path.join(constants.newdir, 'AtLeastItsSomething.csv'))


def removeDOI():
	# remove all DOI files from the directory, in case there was some error in processing the DOIs
	for file in os.listdir(constants.newdir):
		if not file.endswith('.csv'):
			for innerfile in os.listdir(os.path.join(constants.newdir, file)):
				if (innerfile.startswith('DOI_')):
					os.remove(os.path.join(constants.newdir, file, innerfile))
					print('removed ' + file + "'s " + innerfile)


def examinePathogens():
	# examine which pathogens have DOIs/abstracts, and which don't.
	numWithoutAbstract = 0
	numWithoutDOI = 0
	pathogenCount = 0
	hasAbstract = False
	hasDOI = False
	for file in os.listdir(constants.newdir):
		if not file.endswith('.csv') and not file.startswith('Influenza'):
			pathogenCount += 1
			for innerfile in os.listdir(os.path.join(constants.newdir, file)):
				if (innerfile.startswith('DOI_')):
					hasDOI = True
				elif (innerfile.startswith('pubmedAbstract')):
					hasAbstract = True
			if not hasAbstract:
				numWithoutAbstract += 1
			if not hasDOI:
				numWithoutDOI += 1
		hasAbstract = False
		hasDOI = False
	print("Pathogen Count (excluding influenza): " + str(pathogenCount))
	print('number without abstracts: ' + str(numWithoutAbstract))
	print('number without DOI: ' + str(numWithoutDOI))

def main():
	#reformat()
	#appendSuffixes()
	#downloadPMID()
	#removeDOI()
	finishedStatsDOI()
	finishedStatsAbstracts()
	examinePathogens()


if __name__ == "__main__":
	main()
