import constants
import format
import extract
import analyze
import ontologyCompare
import abstractTagger


def main():
	#format.reformat()
	#analyze.remove('TEST')
	#analyze.finishedStatsDOI()
	#analyze.finishedStatsAbstracts()
	#analyze.examinePathogens()
	#ontologyCompare.humanPathogenMerge(constants.mFile)
	#ontologyCompare.mergeOntology()
	abstractTagger.tagAbstracts()

if __name__ == "__main__":
	main()


