import os
import pandas as pd
from pycorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP('http://localhost:9000')

def createClassifierCSV(batchDir):
	tokendf = pd.DataFrame(columns=['sentence_number', 'word', 'pos', 'tag'])
	sentenceNumber = 0
	for textFile in os.listdir(batchDir):
		with open(os.path.join(batchDir, textFile), 'r', encoding='utf-8') as f:
			abstractTokens = nlp.annotate(f.read(), properties={'annotators' : 'pos', 'outputFormat' : 'json'})
		for sentence in abstractTokens['sentences']:
			for token in sentence['tokens']:
				if token['word'] == '<pathogen>':
					tokendf.loc[tokendf.shape[0]-1, 'tag'] = 'PATH'
				elif token['word'] == '<disease>':
					tokendf.loc[tokendf.shape[0]-1, 'tag'] = 'DIS'
				elif token['word'] == '<symptom>':
					tokendf.loc[tokendf.shape[0]-1, 'tag'] = 'SYMP'
				else:
					if token['pos'] == '-RRB-':
						token['word'] = ')'
					elif token['pos'] == '-LRB-':
						token['word'] = '('
					tokendf.loc[tokendf.shape[0]] = [sentenceNumber, token['word'], token['pos'], 'O']
			sentenceNumber += 1
	tokendf.to_csv('ner_dataset.csv')

