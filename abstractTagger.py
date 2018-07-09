import xml.etree.ElementTree as ET
import pandas as pd
from pycorenlp import StanfordCoreNLP
import analyze
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
				v += str(abstractText.text)
		d[key] = v
	pd.DataFrame.from_dict(d, orient='index', columns=['abstract_text']).to_csv('pmabstracts.csv')
	return d

def tagAbstracts():
	d = {}
	forReference = set()
	nlp = StanfordCoreNLP('http://localhost:9000')
	for file in os.listdir('batch'):
		extractAbstractsFromXML(os.path.join('batch', file), d)
	gemdf = pd.read_csv('combined.csv', index_col=0).sort_values(by='pathogen')
	gemdf['pubmed_abstracts'] = ''
	for key in d:
		if d[key] == '':
			continue
		output = nlp.annotate(d[key], properties={
			'annotators': 'pos',
			'outputFormat': 'json'
		})
		print(d[key])
		a = []
		for sentence in output["sentences"]:
			for t in sentence["tokens"]:
				if t["pos"].find("NN") != -1 or t["pos"].find("JJ") != -1:
					if t['pos'] == 'NNS' or t['pos'] == 'NNPS':
						a.append(t['word'][:-1])
						a.append(t['word'][:-2])
					a.append(t["word"].lower())
		a = analyze.unique_list(a)
		b = set()
		c = set()
		for index, row in gemdf.iterrows():
			if row['pathogen'] in b or row['disease'] in c:
				continue
			containsDisease = False
			containsName = False
			for word in a:
				if len(word) < 3:
					continue
				if word.lower() in (str(row['pathogen']).lower().split(' ')):
					containsName = True
					print(str(row['pathogen']))
					print('\t' + word)
				elif word.lower() in analyze.unique_list((str(row['disease']).lower().replace(';', ' ').split(' '))):
					containsDisease = True
					print(str(row['pathogen'] + ': ' + str(row['disease']).lower().replace(';', ' ')))
					print('\t' + word)
			if containsDisease and containsName:
				print('found PMID ' + key + ' matching ' + row['pathogen'])
				row['pubmed_abstracts'] += (str(key) + ';')
				forReference.add(key)
			else:
				if not containsName:
					b.add(row['pathogen'])
				if not containsDisease:
					c.add(row['disease'])
	print('Out of 6000 abstracts, ' + str(len(forReference)) + ' abstracts referenced one or more pathogens.')
	for key in forReference:
		print('\t' + str(key))
	gemdf.to_csv('testcombined.csv')

