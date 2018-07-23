import xml.etree.ElementTree as ET
import pandas as pd
from pycorenlp import StanfordCoreNLP
import os
from shutil import copyfile

nlp = StanfordCoreNLP('http://localhost:9000')
abbrevKey = {}
possibleNameDescriptions = {'cell', 'forest', 'creek', 'river', 'sewage', 'middle',
							'black', 'rat', 'north', 'east', 'south', 'west', 'monkey', 'valley', 'mink',
							'horse', 'lake', 'bridge', 'small', 'island', 'canal', 'hill', 'tick', 'torque', 'delta',
							'edge', 'bat', 'farm', 'palm',
							'white', 'new', 'western', 'eastern',
							'swine', 'reef', 'royal', 'latino',
							'tumor', 'keystone', 'leopard', 'australian', 'american', 'major',
							'human', 'cross', 'ancestor',
							'del', 'victoria', 'fusing', 'subsp', 'co', 'alb', 'as', 'sin',
							'chi', 'var', 'associated', 'rev.', 'high', 'nam', 'cor',
							'tel', 'aus', 'fes', 'tern', 'chr', 'nsw', 'cao', 'ein', 'ross', 'chaoyang',
							'hendra' 'rotterdam',
							'mem', 'tai', 'pac', 'mor', 'indian', 'tick-borne', 'avium', 'influenza',
							'equine', 'vaccinia', 'encephalitis', 'mumps', 'cowpox', 'immunodeficiency', 'whitewater',
							'rift', 'kunjin', 'ill', 'disease'}
possibleNameDescriptionsAdj, possibleDiseaseDescriptionsAdj, possibleSymptomDescriptionsAdj = set(), set(), set()
possibleDiseaseDescriptions = {'appendix', 'bell', 'bite', 'bone', 'breast', 'catheter', 'cord', 'cramp',
							   'crohn', 'crustacean', 'deer', 'ear', 'finger', 'fish', 'flinders', 'food',
							   'foot', 'gas', 'hand', 'inclusion', 'infant', 'line', 'liver',
							   'lung', 'marrow', 'miller', 'fisher', 'mud', 'postpartum', 'protozoa', 'Q',
							   'rainbow', 'relapsing', 'ritter', 'role', 'salmon', 'site', 'snail',
							   'system', 'tissue', 'traveler', 'trout', 'valve', 'zebrafish', 'trout'  'head', 'hip',
							   'infants', 'lines', 'livers', 'lungs', 'sites', 'snails', 'systems', 'tissues',
							   'travelers', 'valves', 'heads', 'hips', 'eyes', 'brains', 'necks', 'animal', 'urine',
							   'brain', 'white', 'western', 'aortic', 'bones', 'catheters', 'cerebral', 'chronic',
							   'corneal', 'crab', 'crustaceans', 'eye', 'fingers', 'fishes', 'flora', 'foods', 'gases',
							   'green', 'hands', 'hidden', 'homosexual', 'human', 'infectious', 'inflammatory', 'mink',
							   'mouth', 'neck', 'potential', 'primary', 'prosthetic', 'pulmonary', 'respiratory',
							   'sclerosing', 'skin', 'spinal', 'surgical', 't-cell', 't-cells', 'tick', 'ticks',
							   'tiger', 'tigers', 'tract', 'tracts', 'urinary', 'viral', 'virus', 'viruses', 'western',
							   'white', 'excess', 'facial', 'feeding', 'shellfish', 'chest', 'crabs'}

possibleSymptomDescriptions = {'ankle', 'arm', 'back', 'blood', 'body', 'brain', 'color', 'chest', 'cornea',
							   'corneal', 'disturbance', 'ears', 'face', 'gag', 'gland',
							   'gum', 'head', 'heart', 'hip', 'jaw', 'joint', 'leg', 'limb', 'lip',
							   'lymph', 'legs', 'limbs', 'lymphocytes', 'milk', 'muscle', 'neck', 'nerve',
							   'organs',
							   'oropharynx', 'abdominal', 'wound', 'wounds',
							   'blood', 'body', 'brain', 'brains', 'diffuse',
							   'faces', 'feed', 'fibrillation', 'flucuations', 'heart', 'intestinal', 'jaw',
							   'jaws', 'low', 'memory', 'organ', 'muscle', 'muscles', 'nasal', 'nerve', 'night',
							   'spleen', 'tendon', 'tone', 'tongue', 'skin', 'motor'}

nameTagIndicators = {'virus', 'complex', 'media', 'agent', 'types', 'variant', 'strain', 'viruses', 'a', 'b', 'c', 'd',
					 'e', 'f', 'cava', 'brevis', 'cdc', 'atcc', 'medium', 'larvae', 'subtype', 'sp.', 'fetus',
					 'thompson', 'janus',
					 'tuberculosis', 'syndrome', 'fever'}
disTagIndicators = {'allergy', 'deficiency', 'disease', 'infection', 'fever', 'media', 'allergies', 'deficiencies',
					'diseases', 'infections', 'fevers', 'collection', 'collections', 'complex', 'complexes', 'western',
					'agent', 'agents', 'significances', 'specimens', 'specimen'}
sympTagIndicators = {'abnormality', 'ache', 'behavior', 'birth', 'consolidation', 'discharge', 'discomfort',
					 'distension',
					 'disturbance', 'dysfunction', 'ears', 'enlargement', 'failure', 'feeding', 'fibrillation',
					 'flexor',
					 'fluctuation', 'gait', 'impairment', 'inability', 'inflammation', 'injection', 'instability',
					 'involvement', 'labor', 'loops', 'loss', 'motility', 'movement', 'nose', 'pain',
					 'pressure', 'palate', 'palsies', 'paralysis', 'behavior', 'behaviors', 'bleeding', 'change',
					 'changes', 'deviation', 'deviations', 'discharges', 'disturbances', 'glands', 'impairment',
					 'impairments', 'inflammation', 'injections', 'intestine', 'intestines', 'movements',
					 'pulse', 'production', 'pressure', 'pupil', 'pupils', 'response', 'responses', 'rhythms', 'rhythm',
					 'sensation', 'sensations', 'speech', 'withdrawal' 'status', 'tendons', 'vision', 'voice', 'voices',
					 'discomfort', 'dysfunctions'}

removeFromDisease = ['syndrome', 'shock', 'abscess', 'lesion', 'cough', 'hemorrhage', 'hemorrhages', 'coughs', 'role',
					 'significance', 'syndromes', 'abscesses', 'lesions', 'patients', 'men', 'patient', 'man',
					 'pathogen', 'pathogens', 'roles', 'potential']
removeFromSymptom = ['eyes', 'fluid', 'membrane', 'nodes', 'onset', ',', 'fluids', 'rate', 'rates', 'the', 'weights']


# extracts all abstracts from the batch file


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
		if v == '':
			continue
		d[key] = v
	pd.DataFrame.from_dict(d, orient='index', columns=['abstract_text']).to_csv('pmabstracts.csv')
	return d


# create row to hold relevant PMIDs
def createDF():
	global abbrevKey
	gemdf = pd.read_csv('unique_full_ontology_plus_symptoms.csv').sort_values(by='pathogen').reset_index(drop=True)
	# annotate all names, add genus abbreviations
	for index, row in gemdf.iterrows():
		if row['pathogen'].lower().startswith('sars'):
			row['pathogen'] += ' severe acute respiratory syndrome'.upper()
			if 'SARS' not in abbrevKey:
				abbrevKey['SARS'] = set()
			if 'CoV' not in abbrevKey:
				abbrevKey['CoV'] = set()
			abbrevKey['CoV'].add(row['pathogen'])
			abbrevKey['SARS'].add(row['pathogen'])
		elif row['pathogen'].lower().startswith('dengue'):
			row['pathogen'] += ' DENV'
			if 'DENV' not in abbrevKey:
				abbrevKey['DENV'] = set()
			abbrevKey['DENV'].add(row['pathogen'])
		elif row['pathogen'].lower().startswith('zika'):
			row['pathogen'] += ' ZIKV'
			if 'ZIKV' not in abbrevKey:
				abbrevKey['ZIKV'] = set()
			abbrevKey['ZIKV'].add(row['pathogen'])
		elif row['pathogen'].lower().startswith('middle'):
			row['pathogen'] += ' MERS'
			if 'MERS' not in abbrevKey:
				abbrevKey['MERS'] = set()
			if 'CoV' not in abbrevKey:
				abbrevKey['CoV'] = set()
			abbrevKey['CoV'].add(row['pathogen'])
			abbrevKey['MERS'].add(row['pathogen'])
		elif 'ebola' in row['pathogen'].lower():
			row['pathogen'] += ' EBOV'
			if 'EBOV' not in abbrevKey:
				abbrevKey['EBOV'] = set()
			abbrevKey['EBOV'].add(row['pathogen'])
		else:
			abb = abbreviate(row['pathogen'].lower().replace('-', ' ').split(' '))
			row['pathogen'] += (' ' + abb)
			if abb.endswith('V'):
				if abb not in abbrevKey:
					abbrevKey[abb] = set()
				abbrevKey[abb].add(row['pathogen'])
	return gemdf


# def tagThisAbstract(d):
# 	output = nlp.annotate(d, properties={
# 		'annotators': 'pos',
# 		'outputFormat': 'json'
# 	})
# 	print(d)
# 	# Throw out everything but nouns
# 	a = set()
# 	for sentence in output["sentences"]:
# 		for t in sentence["tokens"]:
# 			if t["pos"].find("NN") != -1 or t["pos"].find("FW") != -1:
# 				# if t['word'] in ['virus', 'viruses', 'disease', 'diseases']
# 				if (t['pos'] == 'NNS' or t['pos'] == 'NNPS' or t['pos'] == 'NN'):
# 					a.update([t['word'].lower(), t['word'].lower().split('-')])
# 	return a


def abbreviate(arr):
	global abbrevKey
	needsAppendage = False
	abb = ''
	for word in arr:
		containsletters = True
		for letter in word:
			if not letter.isalpha():
				containsletters = False
		if word == 'SARS':
			return
		if word == 'strain' or not containsletters:
			continue
		if 'virus' in word:
			needsAppendage = True
			if word == 'virus':
				continue
		if len(word) >= 1:
			abb += word[0]
	if needsAppendage:
		abb = abb + 'v'
		return abb.upper()
	else:
		if arr[0][0].isalpha():
			return arr[0][0].upper() + '.'
		return ''


def markFPs(fileName):
	df = pd.read_csv(fileName, index_col=0)
	i = 0
	for index, row in df.iterrows():
		if row['tagged_As'].lower() in {'loss', 'failure', 'failures', 'involvement', 'behavior', 'production',
										'change', 'changes', 'response', 'responses', 'disturbance', 'disturbances',
										'inability', 'fluctuations', 'fluctuation', 'status', 'behaviors'}:
			i += 1
			df.loc[index, 'FPs'] = 1
	df.to_csv(fileName)
	print('num of neitherPosNorNeg for ' + fileName + ': ' + str(i))


def finalProcess(li):
	li[0].to_csv('taggedNames.csv')
	li[1].to_csv('taggedDiseases.csv')
	li[2].to_csv('taggedSymptoms.csv')
	li[3].to_csv('full_ontology_plus_symptoms.csv')
	print('Tagged with pathName and diseaseName: ' + str(li[4]))
	print('Tagged with pathName, diseaseName, and symptomName: ' + str(li[5]))


# def annotateIfNameAndDiseaseExist(d, key, forReference, gemdf, a):
# 	# b: dead names c: dead diseases e: relevant name term g: relevant disease term h: all symptom terms
# 	b = set()
# 	c = set()
# 	nameSet = set()
# 	disSet = set()
# 	sympSet = set()
# 	# iterate through names to place abstract
# 	for index, row in gemdf.iterrows():
# 		# small optimization
# 		if row['pathogen'] in b or row[
# 			'disease'] in c:  # or 'no ' in row['disease'] or row['disease'] == 'nan' or row['disease'] == '':
# 			continue
# 		# set bool values
# 		containsDisease = False
# 		containsName = False
# 		abbrevGenus = False
# 		testabbrev = ''
# 		# iterate through set of unique nouns in abstract
# 		for word in a:
# 			# small optimization
# 			if len(word) < 2:
# 				continue
# 			if abbrevGenus and word[0].islower():
# 				abbrevGenus = False
# 				nameSet.update(testabbrev)
# 			if word.lower().replace(' ', '') in set(str(row['pathogen']).lower().split(' ')):
# 				if len(word) == 2:
# 					abbrevGenus = True
# 					testabbrev = word
# 					continue
# 				if abbrevGenus:
# 					abbrevGenus = False
# 					nameSet.update(testabbrev)
# 				containsName = True
# 				z = [word.lower()]
# 				if len(word) > 5:
# 					z = [word.lower(), word.lower()[:-2] + 'i', word.lower() + 's', word.lower() + 'es',
# 						 word.lower() + 'e', word.lower()[:-1], word.lower()[:-2]]
# 				# print(word)
# 				nameSet.update(z)
# 				if '.' in nameSet:
# 					nameSet.remove('.')
# 			elif word.lower() in set(
# 					str(row['disease']).lower().split(' ')) and word != 'no' and word.lower() not in nameSet:
# 				abbrevGenus = False
# 				testabbrev = ''
# 				# append disease and related plurals to relevant disease term list
# 				containsDisease = True
# 				# print(word)
# 				z = [word.lower(), word.lower()[:-2] + 'i', word.lower() + 's', word.lower() + 'es', word.lower() + 'e',
# 					 word.lower()[:-1], word.lower()[:-2]]
# 				disSet.update(z)
# 			abbrevGenus = False
# 			testabbrev = ''
#
# 		if containsDisease and containsName:
# 			# append relevant PMID to final DF
# 			row['pubmed_abstracts'] += (str(key) + ';')
# 			forReference.add(key)
# 			# annotate all symptom POS, keep all nouns and alter for plurals
# 			if os.path.isfile(os.path.join(row['links'], 'symptoms.txt')):
# 				with open(os.path.join(row['links'], 'symptoms.txt'), 'r', encoding='utf-8') as f:
# 					outputSymptoms = nlp.annotate(f.read(), properties={
# 						'annotators': 'pos',
# 						'outputFormat': 'json'
# 					})
# 				for sentence in outputSymptoms["sentences"]:
# 					for t in sentence["tokens"]:
# 						if t["pos"].find("NN") != -1 or t["pos"].find("FW") != -1:
# 							if (t['pos'] == 'NNS' or t['pos'] == 'NNPS') and len(t['word']) > 5:
# 								sympSet.update([t['word'][:-1], t['word'][:-2]])
# 							elif t['pos'] == 'NN':
# 								sympSet.update(
# 									[t['word'] + 's', t['word'] + 'es', t['word'] + 'e', t['word'][:-2] + 'i'])
# 							sympSet.add(t["word"].lower())
# 			# to avoid repetition/inconsistent tagging, first collect all symptoms relevant
# 			# at this point, we're free to start the tagging process
# 			print('found PMID ' + key + ' matching ' + row['pathogen'])
# 			print(nameSet)
# 			if os.path.exists(os.path.join(row['links'], 'TEST' + key + 'abstract.txt')):
# 				with open(os.path.join(row['links'], 'TEST' + key + 'abstract.txt'), 'r', encoding='utf-8') as f:
# 					text = f.read()
# 			else:
# 				text = d[key]
# 			with open(os.path.join(row['links'], 'TEST' + key + 'abstract.txt'), 'w', encoding='utf-8') as f:
# 				for word in text.split():
# 					test = word.replace('.', '').replace(';', '').replace(':', '').replace(',', '').replace(')',
# 																											'').replace(
# 						'(', '').replace(' ', '').replace('[', '').replace(']', '').replace('<', '').replace('>',
# 																											 '').lower()
# 					# bug caused by the NLP: '(' characters treated as separate words
# 					if test in nameSet:
# 						f.write(word + '<pathogen>' + ' ')
# 					elif test in disSet:
# 						f.write(word + '<disease>' + ' ')
# 					elif test in sympSet:
# 						f.write(word + '<symptom>' + ' ')
# 					else:
# 						f.write(word + ' ')
# 				f.write('\n')
# 		nameSet.clear()
# 		disSet.clear()
# 		sympSet.clear()
# 		if not containsName:
# 			b.add(row['pathogen'])
# 		if not containsDisease:
# 			c.add(row['disease'])


def createSets(gemdf):
	sympDict = {}
	nameDict = {}
	disDict = {}
	for index, row in gemdf.iterrows():
		for word in row['pathogen'].split(' '):
			if word.lower() not in nameDict:
				nameDict[word.lower()] = set()
			if word.lower() == 'viruses':
				if 'viruses' not in nameDict:
					nameDict['viruses'] = set()
				nameDict['viruses'].add(str(row['pathogen']))
			nameDict[word.lower()].add(str(row['pathogen']))

		if isinstance(row['disease'], str) and row['disease'] != '':
			outputDisease = nlp.annotate(row['disease'].replace(',', '.').replace(';', '. '), properties={
				'annotators': 'pos',
				'outputFormat': 'json'
			})
			disKeyList = []
			for sentence in outputDisease["sentences"]:
				for t in sentence["tokens"]:
					if t['pos'] == 'IN' or t['pos'] == 'CC':
						continue
					elif t['pos'] == 'JJ':
						disKeyList.append(t['word'].lower())
					elif t["pos"].find("NN") != -1 or t["pos"].find("FW") != -1:
						if (t['pos'] == 'NNS' or t['pos'] == 'NNPS') and len(t['word']) > 5:
							disKeyList.extend([t['word'][:-1].lower(), t['word'][:-2].lower(), t["word"].lower()])
						elif t['pos'] == 'NN':
							disKeyList.extend(
								[t['word'].lower() + 's', t['word'].lower() + 'es', t['word'].lower() + 'e',
								 t['word'][:-2].lower() + 'i', t["word"].lower()])
						else:
							disKeyList.append(t['word'.lower()])
			for i in disKeyList:
				if str(i) not in disDict:
					disDict[str(i)] = set()
				disDict[str(i)].add(str(row['pathogen']))

		if isinstance(row['symptoms'], str) and row['symptoms'] != '':
			outputSymptoms = nlp.annotate(row['symptoms'], properties={
				'annotators': 'pos',
				'outputFormat': 'json'
			})
			sympKeyList = []
			for sentence in outputSymptoms["sentences"]:
				for t in sentence["tokens"]:
					if t['pos'] == 'IN':
						continue
					elif t['pos'] == 'JJ':
						sympKeyList.append(t['word'].lower())
					if (t['pos'] == 'NNS' or t['pos'] == 'NNPS') and len(t['word']) > 5:
						sympKeyList.extend([t['word'][:-1].lower(), t['word'][:-2].lower()])
					elif t['pos'] == 'NN':
						sympKeyList.extend([t['word'].lower() + 's', t['word'].lower() + 'es', t['word'].lower() + 'e',
											t['word'][:-2].lower() + 'i'])
					sympKeyList.append(t['word'].lower())
			for i in sympKeyList:
				if str(i) not in sympDict:
					sympDict[str(i)] = set()
				sympDict[str(i)].add(str(row['pathogen']))

	if len(disDict) == 0:
		raise Exception('invalid dis length')
	if len(sympDict) == 0:
		raise Exception('invalid symp length')

	for i in removeFromDisease:
		disDict.pop(i, None)
	for i in removeFromSymptom:
		sympDict.pop(i, None)
	# remainNameDis = nameDict.keys() & disDict.keys()
	# remainDisSymp = disDict.keys() & sympDict.keys()
	# remainNameSymp = nameDict.keys() & sympDict.keys()
	# for i in remainNameSymp:
	# 	sympDict.pop(i, None)
	# for i in remainDisSymp:
	# 	sympDict.pop(i, None)
	# for i in remainNameDis:
	# 	disDict.pop(i, None)
	return [nameDict, disDict, sympDict, gemdf]


def createTag(d, key, tag, conditional=''):
	s = '<' + tag + ': '
	if conditional == '':
		for i in d[key]:
			s += str(i) + ','
		return s[:-1] + '>'
	else:
		s1 = set(d[key])
		s2 = set(d[conditional])
		s3 = set.intersection(s1, s2)
		if len(s3) == 0:
			return ''
		for i in s3:
			s += str(i) + ','
		return s[:-1] + '>'


def createNameChain(d, key, arr=set(), conditional=''):
	s = ''
	if conditional == '':
		for i in d[key]:
			s += i + ','
		arr.update(s.split(','))
		return [s[:-2], arr]
	else:
		s1 = set(d[key])
		s2 = set(d[conditional])
		s3 = set.intersection(s1, s2)
		if len(s3) == 0:
			return ''
		for i in s3:
			s += str(i) + ','
			arr.add(s)
		return [s[:-2], arr]


# reminder to self, all i did last night was put in the change for the adjective names...and the POS not tagging
def JumpLandTagger(d, li):
	global possibleNameDescriptions, possibleNameDescriptionsAdj, possibleDiseaseDescriptions, possibleSymptomDescriptionsAdj, possibleDiseaseDescriptionsAdj, possibleSymptomDescriptions
	namedf, disdf, sympdf = pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(
		columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As'])
	nameDict, disDict, sympDict, gemdf, numTag, numAll, numDisSymp, numPathSymp = li[0], li[1], li[2], li[3], 0, 0, 0 ,0
	for key in d:
		possibleDiseaseDescriptionsAdj, possibleNameDescriptionsAdj, possibleDiseaseDescriptionsAdj = set(), set(), set()
		with open(os.path.join('taggedbatch', key + '.txt'), 'w', encoding='utf-8') as f:
			output = nlp.annotate(d[key], properties={
				'annotators': 'pos,ner',
				'outputFormat': 'json'
			})
			hasPath, hasDis, hasSymp, prevWord, pathTaggedList = False, False, False, '', set()
			for sentence in output["sentences"]:
				for t in sentence["tokens"]:
					disTagged, pathTagged, sympTagged = False, False, False
					word = t['word']
					if (t['ner'] == 'LOCATION' or t['ner'] == 'COUNTRY' or t['ner'] == 'STATE_OR_PROVINCE' or t[
						'ner'] == 'CITY'):
						if word in nameDict:
							possibleNameDescriptions.add(word.lower())
						if word in disDict:
							possibleDiseaseDescriptions.add(word.lower())
						if word in sympDict:
							possibleSymptomDescriptions.add(word.lower())
						# if word in sympDict:
						# 	possibleSymptomDescriptions.add(word.lower())
						f.write(' ' + word)
						prevWord = word
						continue
					elif t['pos'] == 'JJ':
						if word in nameDict:
							possibleNameDescriptionsAdj.add(word.lower())
						if word in disDict:
							possibleDiseaseDescriptionsAdj.add(word.lower())
						if word in sympDict:
							possibleSymptomDescriptionsAdj.add(word.lower())
						f.write(' ' + word)
						prevWord = word
						continue
					elif t['pos'] == '.' or t['pos'] == ':':
						f.write(word)
						continue
					if t["pos"].find("NN") == -1 and t["pos"].find("FW") == -1:
						f.write(' ')
						if t['pos'] != 'POS':
							prevWord = word
						else:
							prevWord = ''
						f.write(word)
						continue
					# tagging previous entries, if they depend on this entry (look ahead)
					elif (word.lower() in nameDict and prevWord.lower() in nameDict and
						  (prevWord.lower() in possibleNameDescriptions | possibleNameDescriptionsAdj)) and createTag(
						nameDict, prevWord.lower(), 'pathogen', word.lower()) != '':
						f.write(createTag(nameDict, prevWord.lower(), 'pathogen', word.lower()) + " ")
						chain = createNameChain(nameDict, prevWord.lower(), pathTaggedList, word.lower())
						namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), prevWord]
						pathTaggedList = chain[1]
					elif (word.lower() in disDict and prevWord.lower() in disDict and prevWord.lower() in (
							possibleDiseaseDescriptions | possibleDiseaseDescriptionsAdj
					)) and createTag(disDict, prevWord.lower(), 'disease', word.lower()) != '':
						f.write(createTag(disDict, prevWord.lower(), 'disease', word.lower()) + " ")
						disdf.loc[disdf.shape[0]] = [str(key), createNameChain(disDict, prevWord.lower(), set(),
																			   word.lower())[0].replace(',', ';'),
													 prevWord]
					elif (word.lower() in sympDict and prevWord.lower() in sympDict and prevWord.lower() in (
							possibleSymptomDescriptions | possibleSymptomDescriptionsAdj
					)) and createTag(sympDict, prevWord.lower(), 'symptom', word.lower()) != '':
						f.write(createTag(sympDict, prevWord.lower(), 'symptom', word.lower()) + " ")
						sympdf.loc[sympdf.shape[0]] = [str(key), createNameChain(sympDict, prevWord.lower(), set(),
																				 word.lower())[0].replace(',', ';'),
													   prevWord]
					else:
						f.write(' ')
					if word.lower() in nameDict and not pathTagged and not disTagged and not sympTagged:
						if len(word) == 2 and word[1] == '.':
							possibleNameDescriptions.add(word.lower())
							f.write(word)
							prevWord = word
							continue
						elif (
								word.lower() in nameTagIndicators) and prevWord != '' and prevWord.lower() in nameDict and createTag(
							nameDict, word.lower(), 'pathogen', prevWord.lower()) != '':
							f.write(word + createTag(nameDict, word.lower(), 'pathogen', prevWord.lower()))
							chain = createNameChain(nameDict, word.lower(), pathTaggedList, prevWord.lower())
							namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
							pathTaggedList = chain[1]
							hasPath, pathTagged = True, True
						elif (len(word) <= 4 and word.endswith('V')) or word == 'MERS':
							if word in abbrevKey:
								t = abbrevKey[word] & pathTaggedList
								if word in ['HIV', 'DENV', 'EBOV', 'SARS']:
									chain = createNameChain(nameDict, word.lower(), pathTaggedList)
									f.write(word + createTag(nameDict, word.lower(), 'pathogen'))
									namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
									pathTaggedList = chain[1]
									hasPath, pathTagged = True, True
								elif len(t) != 0:
									tag = '<pathogen: '
									while len(t) != 0:
										tag += t.pop() + ','
									tag = tag[:-1] + '>'
									f.write(word + tag)
									namedf.loc[namedf.shape[0]] = [str(key), tag[11:-1], word]
									hasPath, pathTagged = True, True
						elif len(
								word) >= 3 and word.lower() not in possibleNameDescriptions and word.lower() not in nameTagIndicators and not any(
							char in [',', '.'] for char in word):
							f.write(word + createTag(nameDict, word.lower(), 'pathogen'))
							chain = createNameChain(nameDict, word.lower(), pathTaggedList)
							namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
							pathTaggedList = chain[1]
							hasPath, pathTagged = True, True
					# deal with disease entries
					if word.lower() in disDict and not pathTagged and not disTagged and not sympTagged:
						if (
								word.lower() in disTagIndicators) and prevWord != '' and prevWord.lower() in disDict and createTag(
							disDict, word.lower(), 'disease', prevWord.lower()) != '':
							f.write(word + createTag(disDict, word.lower(), 'disease', prevWord.lower()))
							disdf.loc[disdf.shape[0]] = [str(key), createNameChain(disDict, word.lower(), set(),
																				   prevWord.lower())[0].replace(',',
																												';'),
														 word]
							hasDis, disTagged = True, True
						elif len(
								word) > 3 and word.lower() not in disTagIndicators and word.lower() not in possibleDiseaseDescriptions:
							f.write(word + createTag(disDict, word.lower(), 'disease'))
							disdf.loc[disdf.shape[0]] = [str(key),
														 createNameChain(disDict, word.lower())[0].replace(',', ';'),
														 word]
							hasDis, disTagged = True, True
					if word.lower() in sympDict and not pathTagged and not disTagged and not sympTagged:
						if (
								word.lower() in sympTagIndicators) and prevWord != '' and prevWord.lower() in sympDict and createTag(
							sympDict, word.lower(), 'symptom', prevWord.lower()) != '':
							f.write(word + createTag(sympDict, word.lower(), 'symptom', prevWord.lower()))
							sympdf.loc[sympdf.shape[0]] = [str(key), createNameChain(sympDict, word.lower(), set(),
																					 prevWord.lower())[0].replace(',',
																												  ';'),
														   word]
							hasSymp, sympTagged = True, True
						elif len(
								word) > 3 and word.lower() not in sympTagIndicators and word.lower() not in possibleSymptomDescriptions:
							f.write(word + createTag(sympDict, word.lower(), 'symptom'))
							sympdf.loc[sympdf.shape[0]] = [str(key),
														   createNameChain(sympDict, word.lower())[0].replace(',', ';'),
														   word]
							hasSymp, sympTagged = True, True

					if ('virus' in word or 'bacteria' in word) and (
							not pathTagged and not disTagged and not sympTagged):
						f.write(word + '<pathogen>')
						namedf.loc[namedf.shape[0]] = [str(key), '', word]
					elif word in ['disease', 'diseases', 'infection', 'infections']:
						f.write(word + '<disease>')
						disdf.loc[disdf.shape[0]] = [str(key), '', word]
					elif not pathTagged and not disTagged and not sympTagged:
						f.write(word)
					prevWord = word
		if hasPath and hasDis and not hasSymp:
			numTag += 1
			copyfile(os.path.join('taggedbatch', str(key) + '.txt'), os.path.join('namedisbatch',  str(key) + '.txt'))
		elif hasPath and hasDis and hasSymp:
			numAll += 1
			copyfile(os.path.join('taggedbatch', str(key) + '.txt'), os.path.join('allbatch',  str(key) + '.txt'))
		elif hasPath and hasSymp and not hasDis:
			copyfile(os.path.join('taggedbatch', str(key) + '.txt'), os.path.join('namesympbatch',  str(key) + '.txt'))
			numPathSymp += 1
		elif hasDis and hasSymp and not hasPath:
			copyfile(os.path.join('taggedbatch', str(key) + '.txt'), os.path.join('dissympbatch',  str(key) + '.txt'))
			numDisSymp += 1
		print('now tagging ' + str(key) + '.txt.')
	return [namedf, disdf, sympdf, gemdf, numTag, numAll]


def throwJJTagging(d, li):
	namedf, disdf, sympdf = pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(
		columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As'])
	nameDict, disDict, sympDict, gemdf, numTag, numAll = li[0], li[1], li[2], li[3], 0, 0
	for key in d:
		with open(os.path.join('taggedbatch', key + '.txt'), 'w', encoding='utf-8') as f:
			output = nlp.annotate(d[key], properties={
				'annotators': 'pos,ner',
				'outputFormat': 'json'
			})
			hasPath, hasDis, hasSymp, prevWord = False, False, False, ''
			for sentence in output["sentences"]:
				for t in sentence["tokens"]:
					word = t['word']
					if t['pos'] == '.' or t['pos'] == ':':
						f.write(word)
						continue
					if t["pos"].find("NN") == -1 and t["pos"].find("FW") == -1 or t['ner'] == 'LOCATION' or t[
						'ner'] == 'COUNTRY' or t['ner'] == 'STATE_OR_PROVINCE' or t[
						'ner'] == 'CITY':
						if t['pos'] != 'POS':
							f.write(' ')
						f.write(word)
						continue
					# tagging previous entries, if they depend on this entry (look ahead)
					if word.lower() in nameDict:
						f.write(word + createTag(nameDict, word.lower(), 'pathogen'))
						chain = createNameChain(nameDict, word.lower())
						namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
						hasPath = True
					# deal with disease entries
					elif word.lower() in disDict:
						f.write(word + createTag(disDict, word.lower(), 'disease'))
						disdf.loc[disdf.shape[0]] = [str(key),
													 createNameChain(disDict, word.lower())[0].replace(',', ';'),
													 word]
						hasDis = True
					elif word.lower() in sympDict:
						f.write(word + createTag(sympDict, word.lower(), 'symptom'))
						sympdf.loc[sympdf.shape[0]] = [str(key),
													   createNameChain(sympDict, word.lower())[0].replace(',', ';'),
													   word]
						hasSymp = True

					else:
						f.write(word)
		if hasPath and hasDis and not hasSymp:
			numTag += 1
		elif hasPath and hasDis and hasSymp:
			numAll += 1
		print('now tagging ' + str(key) + '.txt.')
	return [namedf, disdf, sympdf, gemdf, numTag, numAll]


def afterJJthrow(d, li):
	namedf, disdf, sympdf = pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(
		columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As'])
	nameDict, disDict, sympDict, gemdf, numTag, numAll = li[0], li[1], li[2], li[3], 0, 0
	for key in d:
		with open(os.path.join('taggedbatch', key + '.txt'), 'w', encoding='utf-8') as f:
			output = nlp.annotate(d[key], properties={
				'annotators': 'pos,ner',
				'outputFormat': 'json'
			})
			hasPath, hasDis, hasSymp, prevWord = False, False, False, ''
			for sentence in output["sentences"]:
				for t in sentence["tokens"]:
					word = t['word']
					if t['pos'] == '.' or t['pos'] == ':':
						f.write(word)
						continue
					if t["pos"].find("NN") == -1 and t["pos"].find("FW") == -1:
						if t['pos'] != 'POS':
							f.write(' ')
						f.write(word)
						continue
					# tagging previous entries, if they depend on this entry (look ahead)
					if word.lower() in nameDict:
						f.write(word + createTag(nameDict, word.lower(), 'pathogen'))
						chain = createNameChain(nameDict, word.lower())
						namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
						hasPath = True
					# deal with disease entries
					elif word.lower() in disDict:
						f.write(word + createTag(disDict, word.lower(), 'disease'))
						disdf.loc[disdf.shape[0]] = [str(key),
													 createNameChain(disDict, word.lower())[0].replace(',', ';'),
													 word]
						hasDis = True
					elif word.lower() in sympDict:
						f.write(word + createTag(sympDict, word.lower(), 'symptom'))
						sympdf.loc[sympdf.shape[0]] = [str(key),
													   createNameChain(sympDict, word.lower())[0].replace(',', ';'),
													   word]
						hasSymp = True
					else:
						f.write(word)
		if hasPath and hasDis and not hasSymp:
			numTag += 1
		elif hasPath and hasDis and hasSymp:
			numAll += 1
		print('now tagging ' + str(key) + '.txt.')
	return [namedf, disdf, sympdf, gemdf, numTag, numAll]


def oldTagging(d, li):
	namedf, disdf, sympdf = pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(
		columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As'])
	nameDict, disDict, sympDict, gemdf, numTag, numAll = li[0], li[1], li[2], li[3], 0, 0
	for key in d:
		with open(os.path.join('taggedbatch', key + '.txt'), 'w', encoding='utf-8') as f:
			output = nlp.annotate(d[key], properties={
				'annotators': 'pos',
				'outputFormat': 'json'
			})
			hasPath, hasDis, hasSymp, prevWord = False, False, False, ''
			for sentence in output["sentences"]:
				for t in sentence["tokens"]:
					word = t['word']
					if t['pos'] == '.' or t['pos'] == ':':
						f.write(word)
						continue
					if t["pos"].find("NN") == -1 and t["pos"].find("FW") == -1 and t['pos'].find('JJ') == -1:
						if t['pos'] != 'POS':
							f.write(' ')
						f.write(word)
						continue
					# tagging previous entries, if they depend on this entry (look ahead)
					if word.lower() in nameDict:
						f.write(word + createTag(nameDict, word.lower(), 'pathogen'))
						chain = createNameChain(nameDict, word.lower())
						namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
						hasPath = True
					# deal with disease entries
					elif word.lower() in disDict:
						f.write(word + createTag(disDict, word.lower(), 'disease'))
						disdf.loc[disdf.shape[0]] = [str(key),
													 createNameChain(disDict, word.lower())[0].replace(',', ';'),
													 word]
						hasDis = True
					elif word.lower() in sympDict:
						f.write(word + createTag(sympDict, word.lower(), 'symptom'))
						sympdf.loc[sympdf.shape[0]] = [str(key),
													   createNameChain(sympDict, word.lower())[0].replace(',', ';'),
													   word]
						hasSymp = True
					else:
						f.write(word)
		if hasPath and hasDis and not hasSymp:
			numTag += 1
		elif hasPath and hasDis and hasSymp:
			numAll += 1

		print('now tagging ' + str(key) + '.txt.')
	return [namedf, disdf, sympdf, gemdf, numTag, numAll]


def getIntersections(li):
	gemdf = li[3]
	nameset = set()
	disset = set()
	sympset = set()
	for index, row in gemdf.iterrows():
		nameset.update(str(row['pathogen']).lower().split())
		disset.update(str(row['disease']).lower().replace(';', ' ').replace(',', '').split())
		sympset.update(str(row['symptoms']).lower().split())
	namedisSet = set.intersection(nameset, disset)
	dissympSet = set.intersection(disset, sympset)
	namesympSet = set.intersection(nameset, sympset)
	allSet = set.intersection(nameset, disset, sympset)
	with open('namedis.txt', 'a', encoding='utf-8') as f:
		for i in namedisSet:
			f.write(i + '\n')
	with open('dissymp.txt', 'a', encoding='utf-8') as f:
		for i in dissympSet:
			f.write(i + '\n')
	with open('namesymp.txt', 'a', encoding='utf-8') as f:
		for i in namesympSet:
			f.write(i + '\n')
	with open('allset.txt', 'a', encoding='utf-8') as f:
		for i in allSet:
			f.write(i + '\n')


# tag all abstracts extracted from the XML
def tagAbstracts():
	# create dict of PMID/abstract pairs
	d = {}
	# for file in os.listdir('batch'):
	# 	if not file.startswith('test'):
	# 		extractAbstractsFromXML(os.path.join('batch', file), d)
	extractAbstractsFromXML(os.path.join('batch', 'pubmed_batch_0_to_999.xml'), d)
	gemdf = createDF()
	li = createSets(gemdf)
	# getIntersections(li)
	li = JumpLandTagger(d, li)
	# final processing
	finalProcess(li)


def tagAbstractsPlaces():
	d = {}
	# for file in os.listdir('batch'):
	# 	if not file.startswith('test'):
	# 		extractAbstractsFromXML(os.path.join('batch', file), d)
	extractAbstractsFromXML(os.path.join('batch', 'pubmed_batch_0_to_999.xml'), d)
	gemdf = createDF()
	li = createSets(gemdf)
	li = afterJJthrow(d, li)
	#	 final processing
	finalProcess(li)


def tagAbstractsOld():
	d = {}
	# for file in os.listdir('batch'):
	# 	if not file.startswith('test'):
	# 		extractAbstractsFromXML(os.path.join('batch', file), d)
	extractAbstractsFromXML(os.path.join('batch', 'pubmed_batch_0_to_999.xml'), d)

	gemdf = createDF()
	li = createSets(gemdf)
	li = oldTagging(d, li)
	#	 final processing
	finalProcess(li)


def tagAbstractsMid():
	d = {}
	# for file in os.listdir('batch'):
	# 	if not file.startswith('test'):
	# 		extractAbstractsFromXML(os.path.join('batch', file), d)
	extractAbstractsFromXML(os.path.join('batch', 'pubmed_batch_0_to_999.xml'), d)
	gemdf = createDF()
	li = createSets(gemdf)
	li = throwJJTagging(d, li)
	#	 final processing
	finalProcess(li)
