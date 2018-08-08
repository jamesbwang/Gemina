import constants
import pandas as pd
import format
import os
from pycorenlp import StanfordCoreNLP

#merges the human pathogen database with the Gemina/ontology database

def humanPathogenMerge(hFile):
	humdf = pd.read_csv(hFile).sort_values(by='genus').reset_index(drop=True)
	gemdf = pd.read_csv('combined.csv', index_col=0).sort_values(by='pathogen').reset_index(drop=True)

	for index, row in humdf.iterrows():
		if isinstance(row['subspecies'], str):
			name = row['subspecies']
		else:
			name = row['species']
		test = True
		for gemIndex, gemRow in gemdf.iterrows():
			if name.lower().replace(' ', '') == gemRow['pathogen'].lower().replace(' ', ''):
				test = False
				a = str(row['symptoms/diseases']).split(',')
				print('Found ' + name + ' in Gemina, appending...')
				with open(os.path.join(gemRow['links'], 'disease.txt'), 'a', encoding='utf-8') as f:
					for i in a:
						gemdf.loc[gemIndex, 'disease'] = str(gemRow['disease']) + ';' + str(i)
						f.write(' ' + str(i))
		if test:
			print('Did not find ' + name + ' in Gemina, creating...')
			path = os.path.join(constants.NEW_DIR, name.replace(' ', '_').replace(':', ';').replace('?', '!').replace('/', '-').replace('<', 'p').replace('>', 'd'))
			li = [name, '', row['symptoms/diseases'], '', path ,'' ,'' ,'' ,'' ,'']
			if not os.path.exists(path):
				os.makedirs(path)
			if isinstance(row['symptoms/diseases'], str) and row['symptoms/diseases'] != '':
				with open(os.path.join(path, 'disease.txt'), 'w+', encoding='utf-8') as f:
					f.write(row['symptoms/diseases'])
			gemdf.loc[len(gemdf)] = li
	gemdf.to_csv('full_ontology.csv')



#merge the Neo4J OWL query with the Gemina Database to prepare for tagging

def mergeOntology():
	formatter = format.Formatter(constants.OLD_DIR)
	formatter.combineNewCSV()
	gemdf = pd.read_csv('combined.csv')
	ontdf = pd.read_csv(constants.FIRST_ONTOLOGY)
	for index, ontrow in ontdf.iterrows():
		if ontrow['NCBITaxon_label'].lower() not in gemdf['pathogen'].str.lower().tolist():
			o = ontrow['NCBITaxon_label'].replace(' ', '_').replace(':', ';').replace('?', '!').replace('/', '-').replace('<', 'p').replace('>', 'd')
			path = os.path.join(constants.NEW_DIR, o)
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
			g = str(gemdf.iloc[i][0]).replace(' ', '_').replace(':', ';').replace('?', '!').replace('/', '-').replace('<', 'p').replace('>', 'd')
			with open(os.path.join(constants.NEW_DIR, g, 'disease.txt'), 'a', encoding='utf-8') as f:
				f.write(';' + ontrow['DOID_label'].lower())
			print('appended ' + ontrow['DOID_label'] + ' to ' + gemdf.iloc[i][0] + "'s disease.txt")
	gemdf.to_csv('combined.csv')