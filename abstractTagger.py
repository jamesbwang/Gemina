import xml.etree.ElementTree as ET
import pandas as pd
from pycorenlp import StanfordCoreNLP
import os
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

def tagAbstracts():
	d = {}
	forReference = set()
	nlp = StanfordCoreNLP('http://localhost:9000')
	for file in os.listdir('batch'):
		extractAbstractsFromXML(os.path.join('batch', file), d)
	extractAbstractsFromXML(os.path.join('batch', 'testnlp.xml'), d)
	gemdf = pd.read_csv('combined.csv', index_col=0).sort_values(by='pathogen').reset_index(drop=True)
	gemdf['pubmed_abstracts'] = ''
	for key in d:
		if d[key] == '':
			continue
		output = nlp.annotate(d[key], properties={
			'annotators': 'pos',
			'outputFormat': 'json'
		})
		print(d[key])
		a = set()
		for sentence in output["sentences"]:
			for t in sentence["tokens"]:
				if t["pos"].find("NN") != -1 or t["pos"].find("FW") != -1:
					if t['pos'] == 'NNS' or t['pos'] == 'NNPS':
						a.update([t['word'][:-1], t['word'][:-2]])
					elif t['pos'] == 'NN':
						a.update([t['word'] + 's', t['word'] + 'es'])
					a.add(t["word"].lower())
		b = set()
		c = set()
		e = set()
		g = set()
		for index, row in gemdf.iterrows():
			nameOutput = nlp.annotate(str(row['pathogen']), properties={
				'annotators': 'pos',
				'outputFormat': 'json'
			})
			if nameOutput['sentences'][0]['tokens'][0]['pos'] == 'FW' or nameOutput['sentences'][0]['tokens'][0]['pos'] == 'NN' or nameOutput['sentences'][0]['tokens'][0]['pos'] == 'NNP':
				row['pathogen'] += ' ' + str(row['pathogen'][0]) + '.'
		for index, row in gemdf.iterrows():
			if row['pathogen'] in b or row['disease'] in c:
				continue
			containsDisease = False
			containsName = False
			for word in a:
				if len(word) < 3:
					continue
				if word.lower() in set(str(row['pathogen']).lower().split(' ')):
					containsName = True
					#print(str(row['pathogen']))
					z = [word.lower(), word.lower() + 's', word.lower() + 'es', word.lower() + 'e', word.lower()[:-1], word.lower()[:-2]]
					e.update(z)
					#print('\t' + word)
				elif word.lower() in set((str(row['disease']).lower().replace(';', ' ').split(' '))):
					containsDisease = True
					#print(str(row['pathogen'] + ': ' + str(row['disease']).lower().replace(';', ' ')))
					z = [word.lower(), word.lower() + 's', word.lower() + 'es', word.lower() + 'e', word.lower()[:-1], word.lower()[:-2]]
					g.update(z)
					#print('\t' + word)
			if containsDisease and containsName:
				row['pubmed_abstracts'] += (str(key) + ';')
				forReference.add(key)
				if index + 1 != int(gemdf.shape[0]) and row['links'].replace('_', '') == gemdf.loc[index + 1, 'links'].replace('_', ''):
					continue
				print('found PMID ' + key + ' matching ' + row['pathogen'])
				with open(os.path.join(row['links'], 'TESTnewAbstracts.txt'), 'a', encoding='utf-8') as f:
					f.write(key + '\n')
					for word in d[key].split(' '):
						test = word.replace('.', '').replace(';', '').replace(':','').replace(',','').replace(')','').replace('(', '').lower()
						if test in e and len(test) > 3:
							f.write(word + '<pathogen>' + ' ')
						elif test in g and len(test) > 3:
							f.write(word + '<disease>' + ' ')
						else:
							f.write(word + ' ')
					f.write('\n')
				e.clear()
				g.clear()
			else:
				if index + 1 == int(gemdf.shape[0]) or row['links'] != gemdf.loc[index + 1, 'links']:
					e.clear()
					g.clear()
				if not containsName:
					b.add(row['pathogen'])
				if not containsDisease:
					c.add(row['disease'])

	print('Out of 11 abstracts, ' + str(len(forReference)) + ' abstracts referenced one or more pathogens.')
	for key in forReference:
		print('\t' + str(key))
	gemdf.to_csv('TESTtestcombined.csv')
