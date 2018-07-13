import xml.etree.ElementTree as ET
import pandas as pd
from pycorenlp import StanfordCoreNLP
import os

nlp = StanfordCoreNLP('http://localhost:9000')

#extracts all abstracts from the batch file
def extractAbstractsFromXML(file, d):
	tree = ET.parse(file)
	root = tree.getroot()
	for article in root.findall('PubmedArticle'):
		key = ''
		v = ''
		for PMID in article.iter('PMID'):
				key = PMID.text
		for abstract in article.iter('Abstract'):
			for abstractText in abstract.findall('AbstractText'):
				v += ' ' + str(abstractText.text)
		d[key] = v
	pd.DataFrame.from_dict(d, orient='index', columns=['abstract_text']).to_csv('pmabstracts.csv')
	return d

#create row to hold relevant PMIDs
def createDF():
	gemdf = pd.read_csv('full_ontology.csv', index_col=0).sort_values(by='pathogen').reset_index(drop=True)
	gemdf.to_csv('testing.csv')
	gemdf['pubmed_abstracts'] = ''
	#annotate all names, add genus abbreviations
	for index, row in gemdf.iterrows():
		if row['pathogen'].lower().startswith('sars'):
			row['pathogen'] += ' severe acute respiratory syndrome'.upper()
		elif row['pathogen'].lower().startswith('dengue'):
			row['pathogen'] += ' DENV'
			print(row['pathogen'])
			continue
		elif row['pathogen'].lower().startswith('zika'):
			row['pathogen'] += ' ZIKV'
			print(row['pathogen'])
			continue
		elif 'ebola' in row['pathogen'].lower():
			row['pathogen'] += ' EBOV'
			print(row['pathogen'])
			continue
		row['pathogen'] += (' ' + abbreviate(row['pathogen'].lower().replace('-', ' ').split(' ')))
		print(row['pathogen'])
	return gemdf
def tagThisAbstract(d):
	output = nlp.annotate(d, properties={
		'annotators': 'pos',
		'outputFormat': 'json'
	})
	print(d)
	#Throw out everything but nouns
	a = set()
	for sentence in output["sentences"]:
		for t in sentence["tokens"]:
			if t["pos"].find("NN") != -1 or t["pos"].find("FW") != -1:
				#if t['word'] in ['virus', 'viruses', 'disease', 'diseases']
				if (t['pos'] == 'NNS' or t['pos'] == 'NNPS') and len(t['word']) > 5:
					a.update([t['word'][:-1], t['word'][:-2]] + t['word'].split('-'))
				elif t['pos'] == 'NN':
					a.update([t['word'] + 's', t['word'] + 'es', t['word'][:-2] + 'i', t['word'] + 'e'] + t['word'].split('-'))
				a.add(t["word"].lower())
	return a
def abbreviate(arr):
	needsAppendage = False
	abb = ''
	for word in arr:
		containsletters = True
		for letter in word:
			if not letter.isalpha():
				containsletters = False
		if word == 'strain' or not containsletters:
			continue
		if 'virus' in word:
			needsAppendage = True
			if word == 'virus':
				continue
		if len(word) >= 1:
			abb += word[0]
	if needsAppendage:
		abb = abb + ' ' + abb + 'v'
		return abb.upper()
	else:
		if arr[0][0].isalpha():
			return arr[0][0].upper() + '.'
		return ''
def finalProcess(forReference, gemdf, d):
	print('Out of '+ str(len(d)) + ' abstracts, ' + str(len(forReference)) + ' abstracts referenced one or more pathogens.')
	for key in forReference:
		print('\t' + str(key))
	gemdf.to_csv('TESTtestcombined.csv')

def annotateIfNameAndDiseaseExist(d, key, forReference, gemdf, a):
	#b: dead names c: dead diseases e: relevant name term g: relevant disease term h: all symptom terms
	b = set()
	c = set()
	nameSet = set()
	disSet = set()
	sympSet = set()
	#iterate through names to place abstract
	for index, row in gemdf.iterrows():
		#small optimization
		if row['pathogen'] in b or row['disease'] in c: #or 'no ' in row['disease'] or row['disease'] == 'nan' or row['disease'] == '':
			continue
		#set bool values
		containsDisease = False
		containsName = False
		abbrevGenus = False
		testabbrev = ''
		#iterate through set of unique nouns in abstract
		for word in a:
			#small optimization
			if len(word) < 2:
				continue
			if abbrevGenus and word[0].islower():
				abbrevGenus = False
				nameSet.update(testabbrev)
			if word.lower().replace(' ', '') in set(str(row['pathogen']).lower().split(' ')):
				if len(word) == 2:
					abbrevGenus = True
					testabbrev = word
					continue
				if abbrevGenus:
					abbrevGenus = False
					nameSet.update(testabbrev)
				containsName = True
				z = [word.lower()]
				if len(word) > 5:
					z = [word.lower(), word.lower()[:-2] + 'i', word.lower() + 's', word.lower() + 'es', word.lower() + 'e', word.lower()[:-1], word.lower()[:-2]]
				#print(word)
				nameSet.update(z)
				if '.' in nameSet:
					nameSet.remove('.')
			elif word.lower() in set(str(row['disease']).lower().split(' ')) and word != 'no' and word.lower() not in nameSet:
				abbrevGenus = False
				testabbrev = ''
				#append disease and related plurals to relevant disease term list
				containsDisease = True
				#print(word)
				z = [word.lower(), word.lower()[:-2] + 'i', word.lower() + 's', word.lower() + 'es', word.lower() + 'e', word.lower()[:-1], word.lower()[:-2]]
				disSet.update(z)
			abbrevGenus = False
			testabbrev = ''

		if containsDisease and containsName:
			#append relevant PMID to final DF
			row['pubmed_abstracts'] += (str(key) + ';')
			forReference.add(key)
			#annotate all symptom POS, keep all nouns and alter for plurals
			if os.path.isfile(os.path.join(row['links'], 'symptoms.txt')):
				with open(os.path.join(row['links'], 'symptoms.txt'), 'r', encoding='utf-8') as f:
					outputSymptoms = nlp.annotate(f.read(), properties={
						'annotators': 'pos',
						'outputFormat': 'json'
					})
				for sentence in outputSymptoms["sentences"]:
					for t in sentence["tokens"]:
						if t["pos"].find("NN") != -1 or t["pos"].find("FW") != -1:
							if (t['pos'] == 'NNS' or t['pos'] == 'NNPS') and len(t['word']) > 5:
								sympSet.update([t['word'][:-1], t['word'][:-2]])
							elif t['pos'] == 'NN':
								sympSet.update([t['word'] + 's', t['word'] + 'es', t['word'] + 'e', t['word'][:-2] + 'i'])
							sympSet.add(t["word"].lower())
			#to avoid repetition/inconsistent tagging, first collect all symptoms relevant
			#at this point, we're free to start the tagging process
			print('found PMID ' + key + ' matching ' + row['pathogen'])
			print(nameSet)
			if os.path.exists(os.path.join(row['links'], 'TEST' + key + 'abstract.txt')):
				with open(os.path.join(row['links'], 'TEST' + key + 'abstract.txt'), 'r', encoding='utf-8') as f:
					text = f.read()
			else:
				text = d[key]
			with open(os.path.join(row['links'], 'TEST' + key + 'abstract.txt'), 'w', encoding='utf-8') as f:
				for word in text.split():
					test = word.replace('.', '').replace(';', '').replace(':','').replace(',','').replace(')','').replace('(', '').replace(' ','').replace('[', '').replace(']', '').replace('<', '').replace('>', '').lower()
					#bug caused by the NLP: '(' characters treated as separate words
					if test in nameSet:
						f.write(word + '<pathogen>' + ' ')
					elif test in disSet:
						f.write(word + '<disease>' + ' ')
					elif test in sympSet:
						f.write(word + '<symptom>' + ' ')
					else:
						f.write(word + ' ')
				f.write('\n')
		nameSet.clear()
		disSet.clear()
		sympSet.clear()
		if not containsName:
			b.add(row['pathogen'])
		if not containsDisease:
			c.add(row['disease'])
def createSets(gemdf):
	sympSet = set()
	nameSet = set()
	disSet = set()
	for index, row in gemdf.iterrows():
		print('Now on row ' + str(index) + ' out of row ' + str(gemdf.shape[0]))
		outputName = nlp.annotate(str(row['pathogen']), properties={
			'annotators': 'pos',
			'outputFormat': 'json'
		})
		for sentence in outputName["sentences"]:
			for t in sentence["tokens"]:
				if t["pos"].find("NN") != -1 or t["pos"].find("FW") != -1:
					if (t['pos'] == 'NNS' or t['pos'] == 'NNPS') and len(t['word']) > 5:
						nameSet.update([t['word'][:-1].lower(), t['word'][:-2].lower()])
					elif t['pos'] == 'NN':
						nameSet.update([t['word'].lower() + 's', t['word'].lower() + 'es', t['word'].lower() + 'e', t['word'][:-2].lower() + 'i'])
					nameSet.add(t["word"].lower())
		outputDisease = nlp.annotate(str(row['disease']), properties={
			'annotators': 'pos',
			'outputFormat': 'json'
		})
		for sentence in outputDisease["sentences"]:
			for t in sentence["tokens"]:
				if t["pos"].find("NN") != -1 or t["pos"].find("FW") != -1:
					if (t['pos'] == 'NNS' or t['pos'] == 'NNPS') and len(t['word']) > 5:
						disSet.update([t['word'][:-1].lower(), t['word'][:-2].lower()])
					elif t['pos'] == 'NN':
						disSet.update([t['word'].lower() + 's', t['word'].lower() + 'es', t['word'].lower() + 'e', t['word'][:-2].lower() + 'i'])
					disSet.add(t["word"].lower())
		if os.path.isfile(os.path.join(row['links'], 'symptoms.txt')):
			with open(os.path.join(row['links'], 'symptoms.txt'), 'r', encoding='utf-8') as f:
				outputSymptoms = nlp.annotate(f.read(), properties={
					'annotators': 'pos',
					'outputFormat': 'json'
				})
			for sentence in outputSymptoms["sentences"]:
				for t in sentence["tokens"]:
					if t["pos"].find("NN") != -1 or t["pos"].find("FW") != -1:
						if (t['pos'] == 'NNS' or t['pos'] == 'NNPS') and len(t['word']) > 5:
							sympSet.update([t['word'][:-1], t['word'][:-2]])
						elif t['pos'] == 'NN':
							sympSet.update([t['word'] + 's', t['word'] + 'es', t['word'] + 'e', t['word'][:-2] + 'i'])
						sympSet.add(t["word"].lower())
	for key in nameSet:
		with open('names.txt', 'w+', encoding='utf-8') as f:
			f.write(key + ' ')
	for key in disSet:
		with open('disease.txt', 'w+', encoding='utf-8') as f:
			f.write(key + ' ')
	for key in sympSet:
		with open('symps.txt', 'w+', encoding='utf-8') as f:
			f.write(key + ' ')
def tagEverything(d, gemdf):
		if not os.path.isfile('names.txt'):
			createSets(gemdf)
		with open('names.txt', 'r', encoding='utf-8') as f:
			nameSet = set(f.read().split(' '))
		with open('disease.txt', 'r', encoding='utf-8') as f:
			disSet = set(f.read().split(' '))
		with open('symps.txt', 'r', encoding='utf-8') as f:
			sympSet = set(f.read().split(' '))
		for key in d:
			with open(os.path.join('taggedbatch', key + '.txt'), 'w', encoding='utf-8') as f:
				abbrev = False
				output = nlp.annotate(d[key], properties={
					'annotators': 'pos',
					'outputFormat': 'json'
				})
				for sentence in output["sentences"]:
					for t in sentence["tokens"]:
						if t["pos"].find("NN") == -1 and t["pos"].find("FW") == -1:
							f.write(t['word'] + ' ')
							continue
						word = t['word']
						if abbrev and word[0].islower():
							f.write('<pathogen> ')
						else:
							f.write(' ')

						if word.lower() in nameSet:
							if len(word) < 2:
								f.write(word)
							elif len(word) == 2:
								abbrev = True
								f.write(word)
								continue
							else:
								f.write(word + '<pathogen>')
						elif word.lower() in disSet:
							f.write(word + '<disease>')
						elif word.lower() in sympSet:
							f.write(word + '<symptom>')
						else:
							f.write(word)
						abbrev = False
						f.write(' ')
			print('now tagging ' + str(key) + '.txt.')




#tag all abstracts extracted from the XML
def tagAbstracts():
	#create dict of PMID/abstract pairs
	d = {}
	forReference = set()
	for file in os.listdir('batch'):
		if not file.startswith('test'):
			extractAbstractsFromXML(os.path.join('batch', file), d)
	extractAbstractsFromXML(os.path.join('batch', 'testnlp.xml'), d)
	gemdf = createDF()
	# for key in d:
	# 	if d[key] == '':
	# 		continue
	# 	a = tagThisAbstract(d[key])
	# 	annotateIfNameAndDiseaseExist(d, key, forReference, gemdf, a)
	tagEverything(d, gemdf)
	#final processing
	finalProcess(forReference, gemdf, d)
