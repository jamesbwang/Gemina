import constants
import format
import extract
import analyze
import ontologyCompare


def main():
	#format.reformat()
	#analyze.removeDOI()
	#analyze.finishedStatsDOI()
	#analyze.finishedStatsAbstracts()
	#analyze.examinePathogens()
	ontologyCompare.pathogenCompareFirst(constants.firstOntology)

if __name__ == "__main__":
	main()
