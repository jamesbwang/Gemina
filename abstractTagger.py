import xml.etree.ElementTree as ET
import pandas as pd
from pycorenlp import StanfordCoreNLP
import os
import constants
import shutil as sh

class Tagger:
	__nlp = StanfordCoreNLP('http://localhost:9000')
	__abbrevKey = {}
	__possibleNameDescriptions = {'cell', 'forest', 'creek', 'river', 'sewage', 'middle',
								  'black', 'rat', 'north', 'east', 'south', 'west', 'monkey', 'valley', 'mink',
								  'horse', 'lake', 'bridge', 'small', 'island', 'canal', 'hill', 'tick', 'torque',
								  'delta',
								  'edge', 'bat', 'farm', 'palm',
								  'white', 'new', 'western', 'eastern',
								  'swine', 'reef', 'royal', 'latino',
								  'tumor', 'keystone', 'leopard', 'australian', 'american', 'major',
								  'human', 'cross', 'ancestor',
								  'del', 'victoria', 'fusing', 'subsp', 'co', 'alb', 'as', 'sin',
								  'chi', 'var', 'associated', 'rev.', 'high', 'nam', 'cor',
								  'tel', 'aus', 'fes', 'tern', 'chr', 'nsw', 'cao', 'ein', 'ross', 'chaoyang',
								  'hendra' 'rotterdam',
								  'mem', 'tai', 'pac', 'mor', 'indian', 'tick-borne', 'avium',
								  'equine', 'vaccinia', 'mumps', 'cowpox', 'immunodeficiency', 'whitewater',
								  'rift', 'kunjin', 'ill', 'disease', 'fever', 'this', 'equine', 'st.'}
	__possibleDiseaseDescriptions = {'appendix', 'bell', 'bite', 'bone', 'breast', 'catheter', 'cord', 'cramp',
									 'crohn', 'crustacean', 'deer', 'ear', 'finger', 'fish', 'flinders', 'food',
									 'foot', 'gas', 'hand', 'inclusion', 'infant', 'line', 'liver',
									 'lung', 'marrow', 'miller', 'fisher', 'mud', 'postpartum', 'protozoa', 'Q',
									 'rainbow', 'relapsing', 'ritter', 'role', 'salmon', 'site', 'snail',
									 'system', 'tissue', 'traveler', 'trout', 'valve', 'zebrafish', 'trout'  'head',
									 'hip',
									 'infants', 'lines', 'livers', 'lungs', 'sites', 'snails', 'systems', 'tissues',
									 'travelers', 'valves', 'heads', 'hips', 'eyes', 'brains', 'necks', 'animal',
									 'urine',
									 'brain', 'white', 'western', 'aortic', 'bones', 'catheters', 'cerebral', 'chronic',
									 'corneal', 'crab', 'crustaceans', 'eye', 'fingers', 'fishes', 'flora', 'foods',
									 'gases',
									 'green', 'hands', 'hidden', 'homosexual', 'human', 'infectious', 'inflammatory',
									 'mink',
									 'mouth', 'neck', 'potential', 'primary', 'prosthetic', 'pulmonary', 'respiratory',
									 'sclerosing', 'skin', 'spinal', 'surgical', 't-cell', 't-cells', 'tick', 'ticks',
									 'tiger', 'tigers', 'tract', 'tracts', 'urinary', 'viral', 'virus', 'viruses',
									 'western',
									 'white', 'excess', 'facial', 'shellfish', 'chest', 'crabs',
									 'immunodeficiency', 'subacute', 'equine', 'st.', 'western', 'river', 'rivers',
									 'head', 'heads'}

	__possibleSymptomDescriptions = {'ankle', 'arm', 'back', 'blood', 'body', 'brain', 'color', 'chest', 'cornea',
									 'corneal', 'ears', 'face', 'gag', 'gland',
									 'gum', 'head', 'heart', 'hip', 'jaw', 'joint', 'leg', 'limb', 'lip',
									 'lymph', 'legs', 'limbs', 'lymphocytes', 'milk', 'muscle', 'neck', 'nerve',
									 'organs',
									 'oropharynx', 'abdominal',
									 'blood', 'body', 'brain', 'brains', 'diffuse',
									 'faces', 'feed', 'heart', 'intestinal', 'jaw',
									 'jaws', 'low', 'memory', 'organ', 'muscle', 'muscles', 'nasal', 'nerve', 'night',
									 'spleen', 'tendon', 'tone', 'tongue', 'skin', 'motor', 'weight', 'mucosa', 'right',
									 'white', 'coordination', 'arms', 'ankles', 'backs', 'bodies', 'brains', 'colors',
									 'chests', 'faces', 'glands', 'heads', 'hearts', 'hips', 'jaws', 'joints', 'limbs',
									 'lips', 'muscles', 'nerves', 'spleens', 'tendons', 'tongues'}

	__nameTagIndicators = {'virus', 'complex', 'media', 'agent', 'types', 'variant', 'strain', 'viruses', 'a', 'b', 'c',
						   'd',
						   'e', 'f', 'cava', 'brevis', 'cdc', 'atcc', 'medium', 'larvae', 'subtype', 'sp.', 'fetus',
						   'thompson', 'janus', 'syndrome', 'otitis', 'tuberculosis', 'mucosa'}
	__disTagIndicators = {'allergy', 'deficiency', 'disease', 'infection', 'fever', 'media', 'allergies',
						  'deficiencies',
						  'diseases', 'infections', 'fevers', 'collection', 'collections', 'complex', 'complexes',
						  'agent', 'agents', 'significances', 'specimens', 'specimen', 'a', 'b', 'c', 'd', 'e', 'f',
						  'cyst',
						  'cysts'}
	__sympTagIndicators = {'abnormality', 'ache', 'behavior', 'birth', 'consolidation', 'discharge', 'discomfort',
						   'distension',
						   'disturbance', 'dysfunction', 'ears', 'enlargement', 'failure', 'feeding', 'fibrillation',
						   'flexor',
						   'fluctuation', 'gait', 'impairment', 'inability', 'injection', 'instability',
						   'involvement', 'labor', 'loops', 'loss', 'motility', 'movement', 'nose', 'pain',
						   'pressure', 'palate', 'palsies', 'paralysis', 'behavior', 'behaviors', 'bleeding', 'change',
						   'changes', 'deviation', 'deviations', 'discharges', 'disturbances', 'glands', 'impairment',
						   'impairments', 'injections', 'intestine', 'intestines', 'movements',
						   'pulse', 'production', 'pressure', 'pupil', 'pupils', 'response', 'responses', 'rhythms',
						   'rhythm',
						   'sensation', 'sensations', 'speech', 'withdrawal', 'status', 'tendons', 'vision', 'voice',
						   'voices',
						   'dysfunctions', 'tract', 'excess', 'symptom', 'symptoms', 'losses', 'statuses', 'retention',
						   'abnormalities', 'aches', 'behaviors', 'consolidations', 'discharges', 'discomforts',
						   'dysfunctions', 'failures', 'fibrillations', 'fluctuations', 'impairments', 'inabilities',
						   'injections', 'intestines', 'pulses', 'productions', 'pressures', 'statuses', 'tracts',
						   'excesses',
						   'enlargements', 'palates', 'births', 'distensions', 'feedings', 'feather', 'feathers'}

	__removeFromName = {'bacteria', 'era'}
	__removeFromDisease = {'shock', 'abscess', 'lesion', 'cough', 'hemorrhage', 'hemorrhages', 'coughs', 'role',
						   'significance', 'abscesses', 'lesions', 'patients', 'men', 'patient', 'man',
						   'pathogen', 'pathogens', 'roles', 'potential', 'clostridium', 'nodules'}
	__addToSymptoms = {'nodules', 'cyst', 'cysts'}
	__removeFromSymptom = {'eyes', 'pneumonia', 'fluid', 'membrane', 'nodes', 'onset', ',', 'fluids', 'rate', 'rates',
						   'the',
						   'weights', 'coli'}

	# extracts all abstracts from the batch file

	def __extractAbstractsFromXML(self, file, d):
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
		pd.DataFrame.from_dict(d, orient='index', columns=['abstract_text']).to_csv(constants.ABSTRACT_DATA)
		return d

	# create row to hold relevant PMIDs
	def __createDF(self):
		gemdf = pd.read_csv(constants.UNIQUE_ONTOLOGY).sort_values(by='pathogen').reset_index(drop=True)
		# annotate all names, add genus abbreviations
		for index, row in gemdf.iterrows():
			if row['pathogen'].lower().startswith('sars'):
				row['pathogen'] += ' severe acute respiratory syndrome'.upper()
				if 'SARS' not in self.__abbrevKey:
					self.__abbrevKey['SARS'] = set()
				if 'CoV' not in self.__abbrevKey:
					self.__abbrevKey['CoV'] = set()
				self.__abbrevKey['CoV'].add(row['pathogen'])
				self.__abbrevKey['SARS'].add(row['pathogen'])
			elif row['pathogen'].lower().startswith('dengue'):
				row['pathogen'] += ' DENV'
				if 'DENV' not in self.__abbrevKey:
					self.__abbrevKey['DENV'] = set()
				self.__abbrevKey['DENV'].add(row['pathogen'])
			elif row['pathogen'].lower().startswith('zika'):
				row['pathogen'] += ' ZIKV'
				if 'ZIKV' not in self.__abbrevKey:
					self.__abbrevKey['ZIKV'] = set()
				self.__abbrevKey['ZIKV'].add(row['pathogen'])
			elif row['pathogen'].lower().startswith('middle'):
				row['pathogen'] += ' MERS'
				if 'MERS' not in self.__abbrevKey:
					self.__abbrevKey['MERS'] = set()
				if 'CoV' not in self.__abbrevKey:
					self.__abbrevKey['CoV'] = set()
				self.__abbrevKey['CoV'].add(row['pathogen'])
				self.__abbrevKey['MERS'].add(row['pathogen'])
			elif 'ebola' in row['pathogen'].lower():
				row['pathogen'] += ' EBOV'
				if 'EBOV' not in self.__abbrevKey:
					self.__abbrevKey['EBOV'] = set()
				self.__abbrevKey['EBOV'].add(row['pathogen'])
			else:
				abb = self.__abbreviate(row['pathogen'].lower().replace('-', ' ').split(' '))
				row['pathogen'] += (' ' + abb)
				if abb.endswith('V'):
					if abb not in self.__abbrevKey:
						self.__abbrevKey[abb] = set()
					self.__abbrevKey[abb].add(row['pathogen'])
		gemdf.to_csv('unique_full_ontology_plus_symptoms_plus_abbrev.csv')
		return gemdf

	def __abbreviate(self, arr):
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

	def __finalProcess(self, li):
		li[0].to_csv('taggedNames.csv')
		li[1].to_csv('taggedDiseases.csv')
		li[2].to_csv('taggedSymptoms.csv')
		li[3].to_csv('full_ontology_plus_symptoms.csv')
		print('Tagged with pathName and diseaseName: ' + str(li[4]))
		print('Tagged with pathName, diseaseName, and symptomName: ' + str(li[5]))

	def __createSets(self, gemdf):
		sympDict, nameDict, disDict = {}, {}, {}
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
				outputDisease = self.__nlp.annotate(row['disease'].replace(',', '.').replace(';', '. '), properties={
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
						elif t["pos"].find("NN") != -1 or t['pos'] == 'FW':
							if (t['pos'] == 'NNS' or t['pos'] == 'NNPS') and len(t['word']) > 5:
								disKeyList.extend([t['word'][:-1].lower(), t['word'][:-2].lower(), t["word"].lower()])
							elif t['pos'] == 'NN':
								disKeyList.extend(
									[t['word'].lower() + 's', t['word'].lower() + 'es', t['word'].lower() + 'e',
									 t['word'][:-2].lower() + 'i', t["word"].lower()])
							else:
								disKeyList.append(t['word'].lower())
				outputDiseaseList = self.__nlp.annotate('. '.join([x for x in disKeyList]), properties={
					'annotators': 'pos',
					'outputFormat': 'json'
				})
				for s in outputDiseaseList['sentences']:
					for t in s['tokens']:
						if t['pos'] == 'FW':
							disKeyList.remove(t['word'])
				for i in disKeyList:
					if str(i) not in disDict:
						disDict[str(i)] = set()
					disDict[str(i)].add(str(row['pathogen']))
			if isinstance(row['symptoms'], str) and row['symptoms'] != '':
				outputSymptoms = self.__nlp.annotate(row['symptoms'], properties={
					'annotators': 'pos',
					'outputFormat': 'json'
				})
				sympKeyList = []
				for sentence in outputSymptoms["sentences"]:
					for t in sentence["tokens"]:
						if t['pos'] == 'IN' or t['pos'] == 'CC':
							continue
						elif t['pos'] == 'JJ':
							sympKeyList.append(t['word'].lower())
						if (t['pos'] == 'NNS' or t['pos'] == 'NNPS') and len(t['word']) > 5:
							sympKeyList.extend([t['word'][:-1].lower(), t['word'][:-2].lower()])
						elif t['pos'] == 'NN':
							sympKeyList.extend(
								[t['word'].lower() + 's', t['word'].lower() + 'es', t['word'].lower() + 'e',
								 t['word'][:-2].lower() + 'i'])
						sympKeyList.append(t['word'].lower())
				outputSymptomList = self.__nlp.annotate('. '.join([x for x in sympKeyList]), properties={
					'annotators': 'pos',
					'outputFormat': 'json'
				})
				for s in outputSymptomList['sentences']:
					for t in s['tokens']:
						if t['pos'] == 'FW':
							sympKeyList.remove(t['word'])
				for i in sympKeyList:
					if str(i) not in sympDict:
						sympDict[str(i)] = set()
					sympDict[str(i)].add(str(row['pathogen']))
		for i in self.__removeFromName:
			nameDict.pop(i, None)
		for i in self.__removeFromDisease:
			disDict.pop(i, None)
		for i in self.__removeFromSymptom:
			sympDict.pop(i, None)
		for i in self.__addToSymptoms:
			sympDict[i] = set('Manually_moved')
		return [nameDict, disDict, sympDict, gemdf]

	def __createTag(self, d, key, tag, conditional=''):
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

	def __createNameChain(self, d, key, arr=set(), conditional=''):
		s = ''
		if conditional == '':
			for i in d[key]:
				s += i + ','
				arr.add(i)
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
	def __JumpLandTagger(self, d, li):
		namedf, disdf, sympdf = pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(
			columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As'])
		nameDict, disDict, sympDict, gemdf, numTag, numAll, numDisSymp, numPathSymp = li[0], li[1], li[2], li[
			3], 0, 0, 0, 0
		for key in d:
			possibleDiseaseDescriptionsAdj, possibleNameDescriptionsAdj, possibleSymptomDescriptionsAdj = set(), set(), set()
			with open(os.path.join('taggedbatch', key + '.txt'), 'w', encoding='utf-8') as f:
				output = self.__nlp.annotate(d[key], properties={'annotators': 'pos,ner', 'outputFormat': 'json'})
				prevWord, pathTaggedList = '', set()
				for sentence in output["sentences"]:
					for t in sentence["tokens"]:
						disTagged, pathTagged, sympTagged = False, False, False
						word = t['word']
						# tagging previous entries, if they depend on this entry (look ahead)
						if (word.lower() in nameDict and prevWord.lower() in nameDict and (
								prevWord.lower() in self.__possibleNameDescriptions | possibleNameDescriptionsAdj)) and self.__createTag(
								nameDict, prevWord.lower(), 'pathogen', word.lower()) != '':
							f.write('<pathogen>')
							chain = self.__createNameChain(nameDict, prevWord.lower(), pathTaggedList, word.lower())
							# namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), prevWord]
							pathTaggedList = chain[1]

						if (word.lower() in disDict and prevWord.lower() in disDict and prevWord.lower() in (
								self.__possibleDiseaseDescriptions | possibleDiseaseDescriptionsAdj)) and self.__createTag(
								disDict, prevWord.lower(), 'disease', word.lower()) != '':
							f.write('<disease>')
						# disdf.loc[disdf.shape[0]] = [str(key), createNameChain(disDict, prevWord.lower(), set(), word.lower())[0].replace(',', ';'), prevWord]

						if (word.lower() in sympDict and prevWord.lower() in sympDict and prevWord.lower() in (
								self.__possibleSymptomDescriptions | possibleSymptomDescriptionsAdj)) and self.__createTag(
								sympDict, prevWord.lower(), 'symptom', word.lower()) != '':
							f.write('<symptom>')
						# sympdf.loc[sympdf.shape[0]] = [str(key), createNameChain(sympDict, prevWord.lower(), set(), word.lower())[0].replace(',', ';'), prevWord]

						if t['ner'] in ['LOCATION', 'COUNTRY', 'STATE_OR_PROVINCE', 'CITY', 'NATIONALITY',
										'ORGANIZATION',
										'DATE', 'PERSON']:
							if word.lower() in nameDict:
								possibleNameDescriptionsAdj.add(word.lower())
							if word.lower() in disDict:
								possibleDiseaseDescriptionsAdj.add(word.lower())
							if word.lower() in sympDict:
								possibleSymptomDescriptionsAdj.add(word.lower())
							f.write(' ' + word)
							prevWord = word
							continue
						elif t['pos'] == 'JJ':
							if word.lower() in nameDict:
								possibleNameDescriptionsAdj.add(word.lower())
							if word.lower() in disDict:
								possibleDiseaseDescriptionsAdj.add(word.lower())
							if word.lower() in sympDict:
								possibleSymptomDescriptionsAdj.add(word.lower())
							f.write(' ' + word)
							prevWord = word
							continue
						elif t['pos'] == '.' or t['pos'] == ':':
							prevWord = '!!!'
							f.write(word)
							continue
						elif t['pos'] == '-LRB-':
							prevWord = '!!!'
							f.write(' (')
							continue
						elif t['pos'] == '-RRB-':
							prevWord = ''
							f.write(')')
							continue
						if 'NN' not in t['pos'] and t['pos'] != 'FW':
							f.write(' ' + word)
							prevWord = '!!!'
							continue
						f.write(' ' + word)
						if word.lower() in nameDict:
							if len(word) == 2 and word[1] == '.':
								self.__possibleNameDescriptions.add(word.lower())
								prevWord = word
								continue
							elif (
									word.lower() in self.__nameTagIndicators) and prevWord.lower() in nameDict and self.__createTag(
									nameDict, word.lower(), 'pathogen', prevWord.lower()) != '':
								f.write('<pathogen>')
								chain = self.__createNameChain(nameDict, word.lower(), pathTaggedList, prevWord.lower())
								# namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
								pathTaggedList = chain[1]
								pathTagged = True
							elif (len(word) <= 4 and word.endswith('V')) or word == 'MERS':
								if word in self.__abbrevKey:
									combined = (self.__abbrevKey[word] & pathTaggedList)
									if word in {'HIV', 'DENV', 'EBOV', 'SARS'}:
										chain = self.__createNameChain(nameDict, word.lower(), pathTaggedList)
										f.write('<pathogen>')
										# namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
										pathTaggedList = chain[1]
										pathTagged = True
									elif len(combined) != 0:
										# tag = '<pathogen: '
										# while len(combined) != 0:
										# 	tag += combined.pop() + ','
										# tag = tag[:-1] + '>'
										f.write('<pathogen>')
										# namedf.loc[namedf.shape[0]] = [str(key), tag[11:-1], word]
										pathTagged = True
							elif len(
									word) >= 3 and word.lower() not in self.__possibleNameDescriptions and word.lower() not in self.__nameTagIndicators and '.' not in word and ',' not in word:
								f.write('<pathogen>')
								chain = self.__createNameChain(nameDict, word.lower(), pathTaggedList)
								# namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
								pathTaggedList = chain[1]
								pathTagged = True
						# deal with disease entries
						if word.lower() in disDict and not disTagged:
							if (
									word.lower() in self.__disTagIndicators) and prevWord.lower() in disDict and self.__createTag(
									disDict, word.lower(), 'disease', prevWord.lower()) != '':
								# f.write(word + createTag(disDict, word.lower(), 'disease', prevWord.lower()))
								f.write('<disease>')
								# disdf.loc[disdf.shape[0]] = [str(key), createNameChain(disDict, word.lower(), set(),prevWord.lower())[0].replace(',',';'),word]
								disTagged = True
							elif len(
									word) > 3 and word.lower() not in self.__disTagIndicators and word.lower() not in self.__possibleDiseaseDescriptions:
								# f.write(word + createTag(disDict, word.lower(), 'disease'))
								f.write('<disease>')
								# disdf.loc[disdf.shape[0]] = [str(key), createNameChain(disDict, word.lower())[0].replace(',', ';'), word]
								disTagged = True
						if word.lower() in sympDict and not sympTagged:
							if (
									word.lower() in self.__sympTagIndicators) and prevWord.lower() in sympDict and self.__createTag(
									sympDict, word.lower(), 'symptom', prevWord.lower()) != '':
								f.write('<symptom>')
								# sympdf.loc[sympdf.shape[0]] = [str(key), createNameChain(sympDict, word.lower(), set(), prevWord.lower())[0].replace(',', ';'),word]
								sympTagged = True
							elif len(
									word) > 3 and word.lower() not in self.__sympTagIndicators and word.lower() not in self.__possibleSymptomDescriptions:
								# f.write(word + createTag(sympDict, word.lower(), 'symptom'))
								f.write('<symptom>')
								# sympdf.loc[sympdf.shape[0]] = [str(key), createNameChain(sympDict, word.lower())[0].replace(',', ';'),word]
								sympTagged = True
						prevWord = word
						if word.lower() in ['virus',
											'bacteria'] and word.lower() != 'virus' and word.lower() != 'bacteria' and not pathTagged:
							f.write('<pathogen>')
						# namedf.loc[namedf.shape[0]] = [str(key),'',word]
			print('now tagging ' + str(key) + '.txt.')
		self.__removeAmbiguity('taggedbatch')
		sh.rmtree('taggedbatch')
		return [namedf, disdf, sympdf, gemdf, numTag, numAll]

	def __throwJJTagging(self, d, li):
		namedf, disdf, sympdf = pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(
			columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As'])
		nameDict, disDict, sympDict, gemdf, numTag, numAll = li[0], li[1], li[2], li[3], 0, 0
		for key in d:
			with open(os.path.join('taggedbatch', key + '.txt'), 'w', encoding='utf-8') as f:
				output = self.__nlp.annotate(d[key], properties={
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
							f.write(word + self.__createTag(nameDict, word.lower(), 'pathogen'))
							chain = self.__createNameChain(nameDict, word.lower())
							namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
							hasPath = True
						# deal with disease entries
						elif word.lower() in disDict:
							f.write(word + self.__createTag(disDict, word.lower(), 'disease'))
							disdf.loc[disdf.shape[0]] = [str(key),
														 self.__createNameChain(disDict, word.lower())[0].replace(',',
																												  ';'),
														 word]
							hasDis = True
						elif word.lower() in sympDict:
							f.write(word + self.__createTag(sympDict, word.lower(), 'symptom'))
							sympdf.loc[sympdf.shape[0]] = [str(key),
														   self.__createNameChain(sympDict, word.lower())[0].replace(
															   ',', ';'),
														   word]
							hasSymp = True

						else:
							f.write(word)
			print('now tagging ' + str(key) + '.txt.')
		return [namedf, disdf, sympdf, gemdf, numTag, numAll]

	def __afterJJthrow(self, d, li):
		namedf, disdf, sympdf = pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(
			columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As'])
		nameDict, disDict, sympDict, gemdf, numTag, numAll = li[0], li[1], li[2], li[3], 0, 0
		for key in d:
			with open(os.path.join('taggedbatch', key + '.txt'), 'w', encoding='utf-8') as f:
				output = self.__nlp.annotate(d[key], properties={
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
							f.write(word + self.__createTag(nameDict, word.lower(), 'pathogen'))
							chain = self.__createNameChain(nameDict, word.lower())
							namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
							hasPath = True
						# deal with disease entries
						elif word.lower() in disDict:
							f.write(word + self.__createTag(disDict, word.lower(), 'disease'))
							disdf.loc[disdf.shape[0]] = [str(key),
														 self.__createNameChain(disDict, word.lower())[0].replace(',',
																												  ';'),
														 word]
							hasDis = True
						elif word.lower() in sympDict:
							f.write(word + self.__createTag(sympDict, word.lower(), 'symptom'))
							sympdf.loc[sympdf.shape[0]] = [str(key),
														   self.__createNameChain(sympDict, word.lower())[0].replace(
															   ',', ';'),
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

	def __oldTagging(self, d, li):
		namedf, disdf, sympdf = pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(
			columns=['PMID', 'pathNames', 'tagged_As']), pd.DataFrame(columns=['PMID', 'pathNames', 'tagged_As'])
		nameDict, disDict, sympDict, gemdf, numTag, numAll = li[0], li[1], li[2], li[3], 0, 0
		for key in d:
			with open(os.path.join('taggedbatch', key + '.txt'), 'w', encoding='utf-8') as f:
				output = self.__nlp.annotate(d[key], properties={
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
							f.write(word + self.__createTag(nameDict, word.lower(), 'pathogen'))
							chain = self.__createNameChain(nameDict, word.lower())
							namedf.loc[namedf.shape[0]] = [str(key), chain[0].replace(',', ';'), word]
							hasPath = True
						# deal with disease entries
						elif word.lower() in disDict:
							f.write(word + self.__createTag(disDict, word.lower(), 'disease'))
							disdf.loc[disdf.shape[0]] = [str(key),
														 self.__createNameChain(disDict, word.lower())[0].replace(',',
																												  ';'),
														 word]
							hasDis = True
						elif word.lower() in sympDict:
							f.write(word + self.__createTag(sympDict, word.lower(), 'symptom'))
							sympdf.loc[sympdf.shape[0]] = [str(key),
														   self.__createNameChain(sympDict, word.lower())[0].replace(
															   ',', ';'),
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

	def __getIntersections(self, li):
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
	def tagAbstracts(self):
		# create dict of PMID/abstract pairs
		d = {}
		for file in os.listdir('batch'):
			if not file.startswith('test'):
				self.__extractAbstractsFromXML(os.path.join('batch', file), d)
		gemdf = self.__createDF()
		li = self.__createSets(gemdf)
		# getIntersections(li)
		li = self.__JumpLandTagger(d, li)
		# final processing
		self.__finalProcess(li)

	def tagAbstractsPlaces(self):
		d = {}
		# for file in os.listdir('batch'):
		# 	if not file.startswith('test'):
		# 		extractAbstractsFromXML(os.path.join('batch', file), d)
		self.__extractAbstractsFromXML(os.path.join('batch', 'pubmed_batch_0_to_999.xml'), d)
		gemdf = self.__createDF()
		li = self.__createSets(gemdf)
		li = self.__afterJJthrow(d, li)
		#	 final processing
		self.__finalProcess(li)

	def tagAbstractsOld(self):
		d = {}
		# for file in os.listdir('batch'):
		# 	if not file.startswith('test'):
		# 		extractAbstractsFromXML(os.path.join('batch', file), d)
		self.__extractAbstractsFromXML(os.path.join('batch', 'pubmed_batch_0_to_999.xml'), d)

		gemdf = self.__createDF()
		li = self.__createSets(gemdf)
		li = self.__oldTagging(d, li)
		#	 final processing
		self.__finalProcess(li)

	def tagAbstractsMid(self):
		d = {}
		# for file in os.listdir('batch'):
		# 	if not file.startswith('test'):
		# 		extractAbstractsFromXML(os.path.join('batch', file), d)
		self.__extractAbstractsFromXML(os.path.join('batch', 'pubmed_batch_0_to_999.xml'), d)
		gemdf = self.__createDF()
		li = self.__createSets(gemdf)
		li = self.__throwJJTagging(d, li)
		#	 final processing
		self.__finalProcess(li)

	def __removeAmbiguity(self, abstractDirectory):
		df = pd.read_csv('unique_full_ontology_plus_symptoms.csv')
		disSet, sympSet = set(), set()
		for dis in set(df['disease'].str.lower()):
			if type(dis) == str:
				disSet.update(str(dis).replace(';', ', ').split(', '))
		for symp in set(df['symptoms'].str.lower()):
			if type(symp) == str:
				sympSet.update(str(symp).split(', '))
		for abstractFile in os.listdir(abstractDirectory):
			s = ''
			with open(os.path.join(abstractDirectory, abstractFile), 'r', encoding='utf-8') as f:
				ambiguouslyTaggedAbstractText = f.read()
			cleanedTags = []
			for word in ambiguouslyTaggedAbstractText.split(' '):
				if any((x in word) for x in ['<pathogen>', '<disease>', '<symptom>']):
					cleanedTags.append(word)
				else:
					toWrite = ' '.join([x for x in cleanedTags])
					cleantext = toWrite.replace('<pathogen>', '').replace('<disease>', '').replace('<symptom>',
																								   '').replace(')',
																											   '').replace(
						',', '').replace('.', '').replace(';', '').replace(':', '')
					if len(cleanedTags) != 0:
						if len(cleanedTags) == 1 and (self.__nlp.annotate(cleantext, properties={'annotators': 'pos',
																								 'outputFormat': 'json'})[
														  'sentences'][0]['tokens'][0]['pos'] == 'JJ' or len(
								cleantext) == 1):
							toWrite = cleantext
						elif any(x in set(df['pathogen'].str.lower()) for x in
								 [cleantext.lower(), cleantext.lower() + ' 1']):
							toWrite = cleantext.replace(' ', '<pathogen> ') + '<pathogen>'
						elif cleantext.lower() in disSet:
							toWrite = cleantext.replace(' ', '<disease> ') + '<disease>'
						elif cleantext.lower() in sympSet:
							toWrite = cleantext.replace(' ', '<symptom> ') + '<symptom>'
						else:
							cleanerTags = []
							for w in cleanedTags:
								if '<disease>' in w:
									cleanerTags.append(w.replace('<pathogen>', '').replace('<symptom>', ''))
								elif '<pathogen>' in w:
									cleanerTags.append(w.replace('<symptom>', ''))
								else:
									cleanerTags.append(w)
							toWrite = ' '.join([x for x in cleanerTags])
					cleanedTags.clear()
					if toWrite != '':
						s += ' ' + toWrite + ' ' + word
					else:
						s += ' ' + word

			finalDir = 'cleantext'
			if '<pathogen>' in s and '<disease>' in s and '<symptom>' not in s:
				finalDir = 'namedisbatch'
			elif '<pathogen>' in s and not '<disease>' in s and '<symptom>' in s:
				finalDir = 'namesympbatch'
			elif '<pathogen>' not in s and '<disease>' in s and '<symptom>' in s:
				finalDir = 'dissympbatch'
			elif '<pathogen>' in s and '<disease>' in s and '<symptom>' in s:
				finalDir = 'allbatch'
			with open(os.path.join(finalDir, abstractFile), 'w+', encoding='utf-8') as f:
				f.write(s)
