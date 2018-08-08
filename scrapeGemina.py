import constants
import format
import extract
import analyze
import ontologyCompare
import abstractTagger
import nltkTagger
import reformatForNER

def main():
	#formatter = format.Formatter(constants.dir)
	#formatter.reformat()
	#formatter.createUniqueCSV()
	#analyze.finishedStatsDOI()
	#analyze.finishedStatsAbstracts()
	#analyze.examinePathogens()
	#ontologyCompare.mergeOntology()
	#ontologyCompare.humanPathogenMerge(constants.mFile)
	tagger = abstractTagger.Tagger()
	tagger.tagAbstracts()
	#nltkTagger.tagNLTKBatch(constants.NLTKDIR)
	reformatForNER.createClassifierCSV('allbatch')

if __name__ == "__main__":
	main()


