import constants
import pandas as pd
import format
import os
from pycorenlp import StanfordCoreNLP

def pathogenCompareFirst(firstOntology):
	format.combineNewCSV()
	gemdf = pd.read_csv('combined.csv')
	ontdf = pd.read_csv(firstOntology)
	print(ontdf)
	outcomes = pd.DataFrame(columns=['Pathogen', 'Diseases','Ontology Mentions', 'Symptom Mentions', 'Disease Mentions', 'pathogen_not_in_gemina', 'disease_not_in_gemina', 'links'])
	nameCol = []
	disCol = []
	col1 = []
	col2 = []
	col3 = []
	col4 = []
	col5 = []
	i = 0
	for pathogenName in gemdf['pathogen']:
		if pathogenName in nameCol:
			i+= 1
			continue
		nameCol.append(pathogenName)
		disCol.append(gemdf.loc[i]['disease'])
		col5.append(gemdf.loc[i]['links'])

		pathogenName = pathogenName.lower()
		diseaseName = str(gemdf.loc[i]['disease']).lower()
		j = 0
		for testName in ontdf['NCBITaxon_label'].str.lower():
			if testName == pathogenName:
				print('found match: ' + testName)
				j += 1
		col1.append(j)

		j = 0
		for testName in ontdf['DOID_label'].str.lower():
			if diseaseName in testName:
				print('found match: ' + testName)
				j += 1
		col2.append(j)
		i+= 1
	for ontName in ontdf['NCBITaxon_label']:
		if ontName.lower() not in [gemdf['pathogen'].str.lower().tolist()] and ontName not in col3:
			col3.append(ontName)
			print('found ' + ontName + ' in ontology, but not in Gemina')
	while len(col3) < len(nameCol):
		col3.append('')
	for ontName in ontdf['DOID_label']:
		if ontName.lower() not in [str(x).lower() for x in gemdf['disease'].tolist()] and ontName not in col4:
			col4.append(ontName)
			print('found ' + ontName + ' in disease ontology, but not in Gemina')
	while len(col4) < len(nameCol):
		col4.append('')
	outcomes['Pathogen'] = nameCol
	outcomes['Diseases'] = disCol
	outcomes['Ontology Mentions'] = col1
	outcomes['Disease Mentions'] = col2
	outcomes['pathogen_not_in_gemina'] = col3
	outcomes['disease_not_in_gemina'] = col4
	outcomes['links'] = col5
	diseaseCompareSecond([outcomes], constants.secondOntology)


def diseaseCompareSecond(outcomes, secondOntology):
	outcomes = outcomes[0]
	nlp = StanfordCoreNLP('http://localhost:9000')
	col1 = []
	ontdf = pd.read_csv(secondOntology)
	d = outcomes['Diseases'].tolist()
	l = outcomes['links'].tolist()
	dm = outcomes['Disease Mentions'].tolist()
	dnig = outcomes['disease_not_in_gemina'].tolist()

	j = 0
	for gemDisease in d:
		i = 0
		k = 0
		path = l[j]
		j += 1
		if gemDisease == 'Influenza':
			print(str(j) + ': skipping flu')
			col1.append(0)
			continue
		for ontDisease in ontdf['DOID_label'].tolist():
			h = ontdf.loc[i]['HP_ID_label']
			i += 1
			if str(gemDisease).lower() in ontDisease.lower():
				dm[j-1] += 1
				if 'symptoms.txt' in os.listdir(path):
					with open(os.path.join(path, 'symptoms.txt'), 'r', encoding='utf-8') as f:
						s = f.read().lower().replace('\n', ' ').replace('\t', ' ').replace('-', ' ')
					output = nlp.annotate(s, properties={
						'annotators': 'pos',
						'outputFormat': 'json'
					})
					output2 = nlp.annotate(h.lower(), properties={
						'annotators': 'pos',
						'outputFormat': 'json'
					})
					a = []
					b = []
					for sentence in output["sentences"]:
						for t in sentence["tokens"]:
							if t["pos"].find("NN") != -1 or t["pos"].find("JJ") != -1 or t["pos"].find("RB") != -1 or t["pos"].find("VB") != -1:
								a.append(t["word"])
					for sentence in output2["sentences"]:
						for t in sentence["tokens"]:
							if t["pos"].find("NN") != -1 or t["pos"].find("JJ") != -1 or t["pos"].find("RB") != -1 or t["pos"].find("VB") != -1:
								b.append(t["word"])
					for w in a:
						for p in b:
							if p == w:
								print('symptom match found: ' + p + ' in file ' + path)
								k += 1
		print(str(j) + ': ' + str(gemDisease) + ' symptom reference: ' + str(k))
		col1.append(k)

	for ontDisease in ontdf['DOID_label'].tolist():
		if ontDisease not in [str(x).lower() for x in d] and ontDisease not in dnig:
			print('found ' + ontDisease + ' in disease ontology, but not in Gemina')
			i = 0
			while dnig[i] != '':
				i += 1
			dnig[i] = ontDisease
		print('found ' + ontDisease + ' in disease ontology and in Gemina')
	outcomes['Symptom Mentions'] = col1
	outcomes['disease_not_in_gemina'] = dnig
	outcomes['Disease Mentions'] = dm
	outcomes.to_csv('ontOutcomes.csv')


