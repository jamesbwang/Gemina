import constants
import format
import extract
import analyze
import ontologyCompare
import abstractTagger
import nltkTagger

def main():
	#format.reformat()
	#analyze.remove('symptoms')

	#analyze.finishedStatsDOI()
	#analyze.finishedStatsAbstracts()
	#analyze.examinePathogens()
	#ontologyCompare.mergeOntology()
	#ontologyCompare.humanPathogenMerge(constants.mFile)
	#abstractTagger.tagAbstractsOld()
	#abstractTagger.tagAbstractsMid()
	#abstractTagger.markFPs('taggedSymptoms.csv')
	abstractTagger.tagAbstracts()
	#abstractTagger.tagAbstractsPlaces()
	#format.createUniqueCSV()
	nltkTagger.tagNLTKBatch(constants.NLTKDIR)

if __name__ == "__main__":
	main()


