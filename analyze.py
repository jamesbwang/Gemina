import constants
import scipy.spatial.distance as dist
from pycorenlp import StanfordCoreNLP
import pandas as pd
import os


def unique_list(l):
	# used to make a string with no repeating words
	ulist = []
	[ulist.append(x) for x in l if x not in ulist]
	return ulist


#global variables, because functions often modify more than one value
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
		if len(w) <= 3:
			continue
		elif w.endswith('es'):
			a.append(w[:-2])
		elif w.endswith('s'):
			a.append(w[:-1])
		for name in filename.split(" "):
			if name == '.txt':
				continue
			if len(name) == len(w) and dist.hamming([i for i in w], [j for j in name]) * len(w) <= int(len(w) * .2):
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
	if symp != '':
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
	for file in os.listdir(constants.NEW_DIR):
		filename = file.replace('_', ' ')
		filename = filename.replace(';', ':')
		filename = filename.replace('!', '?')
		filename = filename.replace('-', '/')
		if not file.endswith('.csv'):
			for innerFile in os.listdir(os.path.join(constants.NEW_DIR, file)):
				if innerFile.startswith('DOI'):
					i = int(innerFile[4:5])
					if i == 1 and innerFile[5].isdigit():
						i = 10 * i + int(innerFile[5])
					numDOI += 1
					f = open(os.path.join(constants.NEW_DIR, file, innerFile), 'r', encoding='utf-8')
					s = f.read().lower()
					j = checkReference(s, filename.lower(), i, os.path.join(constants.NEW_DIR, file), col1, col2, col3, col4, coldisease)
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
	finishedStats.to_csv(os.path.join(constants.NEW_DIR, 'abstractReviewDOI.csv'))

	#The below provides additional analysis that could be done with Excel.

	# finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	# i = 0
	# col5 = []
	# col6 = []
	# col7 = []
	# col8 = []
	# col9 = []
	# while i < len(col1):
	# 	if col2[i] > 0 and coldisease[i] > 0 and col3[i] > 0 and col4[i] > 0:
	# 		col5.append(col1[i])
	# 		col6.append(col2[i])
	# 		col7.append(col3[i])
	# 		col8.append(col4[i])
	# 		col9.append(coldisease[i])
	# 	i += 1
	# finishedStats['Pathogen'] = col5
	# finishedStats['Name References'] = col6
	# finishedStats['Symptom References'] = col7
	# finishedStats['Toxin References'] = col8
	# finishedStats['Disease References'] = col9
	# finishedStats.set_index('Pathogen', inplace=True)
	#
	# finishedStats.to_csv(os.path.join(constants.newdir, 'allExistDOI.csv'))
	#
	# finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	# i = 0
	# col5 = []
	# col6 = []
	# col7 = []
	# col8 = []
	# col9 = []
	# while i < len(col1):
	# 	if col2[i] > 0 and coldisease[i] > 0 and col3[i] > 0 and col4[i] == -1:
	# 		col5.append(col1[i])
	# 		col6.append(col2[i])
	# 		col7.append(col3[i])
	# 		col8.append(col4[i])
	# 		col9.append(coldisease[i])
	# 	i += 1
	# finishedStats['Pathogen'] = col5
	# finishedStats['Name References'] = col6
	# finishedStats['Symptom References'] = col7
	# finishedStats['Toxin References'] = col8
	# finishedStats['Disease References'] = col9
	# finishedStats.set_index('Pathogen', inplace=True)
	#
	# finishedStats.to_csv(os.path.join(constants.newdir, 'SymptomsExistDOI.csv'))
	# finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	# i = 0
	# col5 = []
	# col6 = []
	# col7 = []
	# col8 = []
	# col9 = []
	# while i < len(col1):
	# 	if col2[i] > 0 and col3[i] == -1 and col4[i] == -1:
	# 		col5.append(col1[i])
	# 		col6.append(col2[i])
	# 		col7.append(col3[i])
	# 		col8.append(col4[i])
	# 		col9.append(coldisease[i])
	# 	i += 1
	# finishedStats['Pathogen'] = col5
	# finishedStats['Name References'] = col6
	# finishedStats['Symptom References'] = col7
	# finishedStats['Toxin References'] = col8
	# finishedStats['Disease References'] = col9
	# finishedStats.set_index('Pathogen', inplace=True)
	#
	# finishedStats.to_csv(os.path.join(constants.newdir, 'OnlyNameDOI.csv'))
	# finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	# i = 0
	# col5 = []
	# col6 = []
	# col7 = []
	# col8 = []
	# col9 = []
	# while i < len(col1):
	# 	if col2[i] > 0 or col3[i] > 0 - 1 or col4[i] > 0 or coldisease[i] > 0:
	# 		col5.append(col1[i])
	# 		col6.append(col2[i])
	# 		col7.append(col3[i])
	# 		col8.append(col4[i])
	# 		col9.append(coldisease[i])
	# 	i += 1
	# finishedStats['Pathogen'] = col5
	# finishedStats['Name References'] = col6
	# finishedStats['Symptom References'] = col7
	# finishedStats['Toxin References'] = col8
	# finishedStats['Disease References'] = col9
	# finishedStats.set_index('Pathogen', inplace=True)
	#
	# finishedStats.to_csv(os.path.join(constants.newdir, 'AtLeastItsSomethingDOI.csv'))


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
	for file in os.listdir(constants.NEW_DIR):
		filename = file.replace('_', ' ').replace(';', ':').replace('!', '?').replace('-', '/')
		if not file.endswith('.csv'):
			numPathogens += 1
			for innerFile in os.listdir(os.path.join(constants.NEW_DIR, file)):
				if innerFile.startswith('DOI'):
					numDOI += 1
				elif innerFile.startswith('pubmed'):
					f = open(os.path.join(os.path.join(constants.NEW_DIR, file), 'pubmedAbstract.txt'), 'r',
							 encoding='utf-8')
					i = 1
					s = ""
					for line in f:
						if line.startswith(str(i) + '. '):
							numPMID += 1
						elif line.startswith('PMID'):
							j = checkReference(s.lower(), filename.lower(), i, os.path.join(constants.NEW_DIR, file), col1, col2, col3, col4, coldisease)
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
	finishedStats.to_csv(os.path.join(constants.NEW_DIR, 'abstractReview.csv'))

	# The below provides additional analysis that could be done with Excel.


	# finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	# i = 0
	# col5 = []
	# col6 = []
	# col7 = []
	# col8 = []
	# col9 = []
	# while i < len(col1):
	# 	if col2[i] > 0 and coldisease[i] > 0 and col3[i] > 0 and col4[i] > 0:
	# 		col5.append(col1[i])
	# 		col6.append(col2[i])
	# 		col7.append(col3[i])
	# 		col8.append(col4[i])
	# 		col9.append(coldisease[i])
	# 	i += 1
	# finishedStats['Pathogen'] = col5
	# finishedStats['Name References'] = col6
	# finishedStats['Symptom References'] = col7
	# finishedStats['Toxin References'] = col8
	# finishedStats['Disease References'] = col9
	# finishedStats.set_index('Pathogen', inplace=True)
	#
	# finishedStats.to_csv(os.path.join(constants.newdir, 'allExist.csv'))
	#
	# finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	# i = 0
	# col5 = []
	# col6 = []
	# col7 = []
	# col8 = []
	# col9 = []
	# while i < len(col1):
	# 	if col2[i] > 0 and coldisease[i] > 0 and col3[i] > 0 and col4[i] == -1:
	# 		col5.append(col1[i])
	# 		col6.append(col2[i])
	# 		col7.append(col3[i])
	# 		col8.append(col4[i])
	# 		col9.append(coldisease[i])
	# 	i += 1
	# finishedStats['Pathogen'] = col5
	# finishedStats['Name References'] = col6
	# finishedStats['Symptom References'] = col7
	# finishedStats['Toxin References'] = col8
	# finishedStats['Disease References'] = col9
	# finishedStats.set_index('Pathogen', inplace=True)
	#
	# finishedStats.to_csv(os.path.join(constants.newdir, 'SymptomsExist.csv'))
	#
	# finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	# i = 0
	# col5 = []
	# col6 = []
	# col7 = []
	# col8 = []
	# col9 = []
	# while i < len(col1):
	# 	if col2[i] > 0 and coldisease[i] > 0 and col3[i] == -1 and col4[i] == -1:
	# 		col5.append(col1[i])
	# 		col6.append(col2[i])
	# 		col7.append(col3[i])
	# 		col8.append(col4[i])
	# 		col9.append(coldisease[i])
	# 	i += 1
	# finishedStats['Pathogen'] = col5
	# finishedStats['Name References'] = col6
	# finishedStats['Symptom References'] = col7
	# finishedStats['Toxin References'] = col8
	# finishedStats['Disease References'] = col9
	# finishedStats.set_index('Pathogen', inplace=True)
	#
	# finishedStats.to_csv(os.path.join(constants.newdir, 'OnlyName.csv'))
	#
	# finishedStats = pd.DataFrame(columns=['Pathogen', 'Name References', 'Symptom References', 'Toxin References', 'Disease References'])
	# i = 0
	# col5 = []
	# col6 = []
	# col7 = []
	# col8 = []
	# col9 = []
	# while i < len(col1):
	# 	if col2[i] > 0 or col3[i] > 0 or col4[i] > 0 or coldisease[i] > 0:
	# 		col5.append(col1[i])
	# 		col6.append(col2[i])
	# 		col7.append(col3[i])
	# 		col8.append(col4[i])
	# 		col9.append(coldisease[i])
	# 	i += 1
	# finishedStats['Pathogen'] = col5
	# finishedStats['Name References'] = col6
	# finishedStats['Symptom References'] = col7
	# finishedStats['Toxin References'] = col8
	# finishedStats['Disease References'] = col9
	# finishedStats = finishedStats.set_index('Pathogen', inplace=True)
	# finishedStats.to_csv(os.path.join(constants.newdir, 'AtLeastItsSomething.csv'))


def remove(startsWith):
	# remove all DOI files from the directory, in case there was some error in processing the DOIs
	for file in os.listdir(constants.NEW_DIR):
		if not file.endswith('.csv'):
			for innerfile in os.listdir(os.path.join(constants.NEW_DIR, file)):
				if innerfile.startswith(startsWith):
					os.remove(os.path.join(constants.NEW_DIR, file, innerfile))
					print('removed ' + file + "'s " + innerfile)


def examinePathogens():
	# examine which pathogens have DOIs/abstracts, and which don't.
	numWithoutAbstract = 0
	numWithoutDOI = 0
	pathogenCount = 0
	hasAbstract = False
	hasDOI = False
	for file in os.listdir(constants.NEW_DIR):
		if not file.endswith('.csv') and not file.startswith('Influenza'):
			pathogenCount += 1
			for innerfile in os.listdir(os.path.join(constants.NEW_DIR, file)):
				if innerfile.startswith('DOI_'):
					hasDOI = True
				elif innerfile.startswith('pubmedAbstract'):
					hasAbstract = True
			if not hasAbstract:
				numWithoutAbstract += 1
			if not hasDOI:
				numWithoutDOI += 1
		hasAbstract = False
		hasDOI = False
	print("Pathogen Count (excluding Influenza): " + str(pathogenCount))
	print('number without abstracts: ' + str(numWithoutAbstract))
	print('number without DOI: ' + str(numWithoutDOI))