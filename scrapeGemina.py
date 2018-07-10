import constants
import format
import extract
import analyze
import ontologyCompare
import abstractTagger


def main():
	#format.reformat()
	analyze.remove('TESTnewAbstracts')
	#analyze.finishedStatsDOI()
	#analyze.finishedStatsAbstracts()
	#analyze.examinePathogens()
	#ontologyCompare.pathogenCompareFirst(constants.firstOntology)
	#ontologyCompare.mergeOntology()

	abstractTagger.tagAbstracts()
if __name__ == "__main__":
	main()


