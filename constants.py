import os

#replace the code below with the pathway to the infections folder
dir=r"C:\Users\WJang\Desktop\Gemina_Project_Pathogens\Gemina_Project_Pathogens\infections"
newdir = os.path.join(dir, 'infections_new')
fileName = ''
d = {}
def setDirectory(name):
	global fileName
	fileName = os.path.join(newdir, name)

def generatePathogenDictionary():
	global d
	for file in os.listdir(newdir):
		f = open(file,'r')
		if not f.name.endswith('.csv'):
			name = f[len(newdir):]
			d[name] = newdir

def getDirectory():
	return fileName

def getPMIDList():
	urlList = []
	for file in os.listdir(newdir):
		f = open(file, 'r')
		if not f.name.endswith('.csv') and os.path.isfile(os.path.join(file.name, "PMID.txt")):
			PMIDfile = open(os.path.join(file.name, "PMID.txt"), 'r')
			for url in PMIDfile:
				urlList.append(url)
	return urlList

def getURLList(path):
	path = os.path.join(path, 'url.txt')
	urlList = []
	file = open(path, 'r')
	for url in file:
		urlList.append(url)
	return urlList