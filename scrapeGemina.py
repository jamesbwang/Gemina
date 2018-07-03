
import format
import extract
import analyze







def main():
	format.reformat()
	format.appendSuffixes()
	extract.downloadPMID()
	analyze.removeDOI()
	analyze.finishedStatsDOI()
	analyze.finishedStatsAbstracts()
	analyze.examinePathogens()


if __name__ == "__main__":
	main()
