import constants
import format
import extract
import analyze
import ontologyCompare
import abstractTagger
import nltkTagger
import reformatForNER

def main():
	#format.reformat()
	#analyze.finishedStatsDOI()
	#analyze.finishedStatsAbstracts()
	#analyze.examinePathogens()
	#ontologyCompare.mergeOntology()
	#ontologyCompare.humanPathogenMerge(constants.mFile)
	#abstractTagger.tagAbstractsOld()
	#abstractTagger.tagAbstractsMid()
	#abstractTagger.markFPs('taggedSymptoms.csv')
	abstractTagger.tagAbstracts()
	#format.createUniqueCSV()
	#nltkTagger.tagNLTKBatch(constants.NLTKDIR)
	abstractTagger.removeAmbiguity('taggedbatch')
	reformatForNER.createClassifierCSV('allbatch')

if __name__ == "__main__":
	main()


