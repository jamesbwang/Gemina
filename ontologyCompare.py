import constants
import pandas as pd
import format
import os
from pycorenlp import StanfordCoreNLP

#incomplete
def humanPathogenCompare(hFile):
	humdf = pd.read_csv(hFile).set_index('superkingdom', drop=False)
	gemdf = pd.read_csv('combined.csv').set_index('pathogen', drop=False)
	gemdict = gemdf.to_dict('index')
	nlp = StanfordCoreNLP('http://localhost:9000')
	patharr = list(set(gemdf['pathogen'].tolist()))
	humPatharr = list(set(humdf['species'].str.lower().tolist()))
	diseasearr = list(set(gemdf['disease'].tolist()))
	humDiseasearr = list(set(humdf['symptoms/diseases'].str.lower().tolist()))
	nameMentions = []
	diseaseMentions = []
	symptomMentions = []
	disNotInGemina = []
	pathNotInGemina = []
	for pathName in patharr:
		if humPatharr.count(pathName.lower()) == 0:
			pathNotInGemina.append(pathName)
		nameMentions.append(humPatharr.count(pathName.lower()))
		if os.path.isfile(os.path.join(gemdict[pathName], 'symptoms.txt')):
			with open(os.path.join(gemdict[pathName], 'symptoms.txt'), 'r', encoding='utf-8') as f:
				s = f.read().lower()

	i = 0
	for disName in diseasearr:
		for humdisName in humDiseasearr:
			if disName.lower() in humdisName:
				i += 1
		diseaseMentions.append(i)


	list = [nameMentions, diseaseMentions, symptomMentions, disNotInGemina, pathNotInGemina]
	pathogenCompare = pd.DataFrame(list, columns=['pathogen', 'name_mentions', 'symptoms mentions', 'disease', 'disease_mentions', 'pathogen_not_in_gemina', 'diseases_not_in_gemina'])
	pathogenCompare.to_csv('humanOntologyOutcomes.csv')


def mergeOntology():
	format.combineNewCSV()
	gemdf = pd.read_csv('combined.csv')
	ontdf = pd.read_csv(constants.firstOntology)
	for index, ontrow in ontdf.iterrows():
		if ontrow['NCBITaxon_label'].lower() not in gemdf['pathogen'].str.lower().tolist():
			o = ontrow['NCBITaxon_label']
			o = o.replace(' ', '_')
			o = o.replace(':', ';')
			o = o.replace('?', '!')
			o = o.replace('/', '-')
			o = o.replace('<', 'p')
			o = o.replace('>', 'd')
			path = os.path.join(constants.newdir, o)
			l = [ontrow['NCBITaxon_label'], '', ontrow['DOID_label'], '', path, '', '', '', '' ,'']
			print('Saved ' + l[0] + ' to ' + path)
			gemdf.loc[len(gemdf)] = l
			if not os.path.exists(path):
				os.makedirs(path)
			with open(os.path.join(path, 'disease.txt'), 'w+', encoding='utf-8') as f:
				f.write(ontrow['DOID_label'])
		else:
			i = gemdf['pathogen'].str.lower().tolist().index(ontrow['NCBITaxon_label'].lower())
			gemdf.iloc[i, 2] = str(gemdf.iloc[i][2]) + ';' + str(ontrow['DOID_label'])
			g = str(gemdf.iloc[i][0])
			g = g.replace(' ', '_')
			g = g.replace(':', ';')
			g= g.replace('?', '!')
			g= g.replace('/', '-')
			g= g.replace('<', 'p')
			g = g.replace('>', 'd')
			with open(os.path.join(constants.newdir, g, 'disease.txt'), 'a', encoding='utf-8') as f:
				f.write(';' + ontrow['DOID_label'].lower())
			print('appended ' + ontrow['DOID_label'] + ' to ' + gemdf.iloc[i][0] + "'s disease.txt")
	gemdf.to_csv('combined.csv')