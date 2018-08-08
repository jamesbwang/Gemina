import pandas as pd
import os
import nltk
import constants


def tagNLTKBatch(directory):
	NLTKDict = nltkConstrictedDict(directory)
	for PMID in NLTKDict:
		writeTags(tagEntities(NLTKDict, PMID), PMID)


def tagEntities(NLTKDict, PMID):
	abstractText = NLTKDict[PMID]
	tokens = nltk.word_tokenize(abstractText)
	taggedTokens = nltk.pos_tag(tokens)
	return nltk.chunk.ne_chunk(taggedTokens, binary=False)


def writeTags(entities, PMID):
	for node in entities:
		with open(os.path.join('newNLTKTestBatch', str(PMID) + '.txt'), 'a', encoding='utf-8') as f:
			if node[0] not in  [':', ',', '.']:
				f.write(' ')
		if type(node) == nltk.Tree:
			words, tags = zip(*node.leaves())
			with open(os.path.join('newNLTKTestBatch', str(PMID) + '.txt'), 'a', encoding='utf-8') as f:
				f.write(' '.join(words) + '<' + node.label() + '>')
		else:
			with open(os.path.join('newNLTKTestBatch', str(PMID) + '.txt'), 'a', encoding='utf-8') as f:
				f.write(node[0])


def abstractDictionary():
	d = {}
	abdf = pd.read_csv(constants.ABSTRACT_DATA, index_col=0)
	for index, row in abdf.iterrows():
		print(str(index))
		d[index] = row['abstract_text']
	return d


def nltkConstrictedDict(directory):
	abstractDict = abstractDictionary()
	constrainedDict = {}
	for textFile in os.listdir(directory):
		if textFile.endswith('.txt') and int(textFile[:-4]) in abstractDict:
			constrainedDict[textFile[:-4]] = abstractDict[int(textFile[:-4])]
	if len(constrainedDict) == 0:
		raise Exception('invalid length')
	return constrainedDict
