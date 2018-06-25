
import constants
import pandas as pd
import os
import requests
import scipy.spatial.distance as dist



def reformat():
    #edit the old Gemina database such that the columns are reformated appropriately
    #create new .csv files, print the beginnings of the new csvs, and eliminate the last col. (will use for links to the folder)
    for filename in os.listdir(constants.dir):
        if filename.endswith(".csv"):
            df = pd.read_table(os.path.join(constants.dir, filename), sep="\t", comment="#", names=['index', 'pathogen','source', 'disease', 'tsource', 'ttype', 'portal', 'infection_atts', 'tatts', 'comments'])
            df.reset_index()
            #print(df.head())
            #add all the abstracts of the paper(or html for now)
            addAbstract(df, filename)
            continue
        else:
            continue


def appendSuffixes():
    for folder in os.listdir(constants.newdir):
        PMIDpath = os.path.join(os.path.join(constants.newdir, folder), 'PMID.txt')
        if(os.path.isfile(PMIDpath)):
            with open(PMIDpath, 'r') as valid:
                if valid.read().__contains__('&retmode=text&rettype=abstract%0A'):
                    valid.close()
                    return
            with open(PMIDpath, 'rb+') as filehandle:
                filehandle.seek(-1, os.SEEK_END)
                filehandle.truncate()
                filehandle.close()
            with open(PMIDpath, 'a', encoding='utf-8') as filename:
                filename.write("&retmode=text&rettype=abstract%0A")
                print("adding suffixes to pubmed links....")
                filename.close()


def addAbstract(file, fileName):
    #for the column infection_tatts, separate the urls and the PMID's: we will treat these two cases separately.
    k = 0
    for v in file['infection_atts']:
        #find the name in the corresponding pathogen column

        #create the name we'll use in the directory
        dirname = file.iloc[k,1]
        dirname = dirname.replace(' ', '_')
        dirname = dirname.replace(':', ';')
        dirname = dirname.replace('?', '!')
        dirname = dirname.replace('/', '-')

        #create the path we'll put the files in, separated by pathogen
        path = os.path.join(constants.newdir, dirname)
        print(path)
        if not os.path.exists(path):
            os.makedirs(path)

        #insert the directory into the dataframe
        file.at[k, 'links'] = path

        k+=1
        #print(name)

        #break down the PMID/URL's, address them accordingly
        if isinstance(v, str):
            addAbstractHelper(v, path)

        PMIDpath = os.path.join(path, 'PMID.txt')
        URLpath = os.path.join(path, 'url.txt')
        #if os.path.isfile(PMIDpath) and os.stat(PMIDpath).st_size != 0:
        #    crawlPMID(path)
         #   open(PMIDpath, 'w').close()
       # if os.path.isfile(URLpath) and os.stat(URLpath).st_size != 0:
       #     crawlURL(path)
       #     open(URLpath, 'w').close()




#create the file we'll insert into the new_infection database
    filepath = os.path.join(constants.newdir, 'new' + fileName)
    print(filepath)
    #convert the dataframe to csv format
    file.to_csv(filepath)



def addAbstractHelper(v, path):
    if len(v) == 0:
        return;

    #address every entry, and store PMIDs, toxins, symptoms, and relevant URLS in the same place.
    while len(v) > 0:
        if v.startswith('URL:'):
            #create the URL file
            v = v[4:]
            count = 0
            while count < len(v) and v[count] != ';':
                count+= 1
            j = v[: count]
            v = v[count:]
        #print('\t' + j)
            newpath = os.path.join(path, 'url.txt')
            with open(newpath, 'a', encoding='utf-8') as file:
                    file.write(j + '\n')
                    file.close()
           #isolate their abstracts
            continue
        if v.startswith('PMID:'):
            #create the PMID file
            v = v[5:]
            count = 0
            while count < len(v) and v[count] != ';':
                count += 1
            j = v[: count]
            v = v[count:]
            newpath = os.path.join(path, 'PMID.txt')
            if os.path.isfile(newpath):
                with open(newpath, 'r', encoding = 'utf-8') as valid:
                    if(valid.read().__contains__(j)):
                        continue
                    with open(newpath, 'a', encoding='utf-8') as file:
                        file.write(j + ',')
                        file.close()

                with open(newpath, 'a', encoding='utf-8') as file:
                        file.write(j + ',')
                        file.close()
            else:
                with open(newpath, 'w', encoding='utf-8') as file:
                    file.write('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=' + j + ',')
                    file.close()

            #isolate their abstracts


        #print('\t' + j)
            continue

        if v.startswith("toxin="):
            v = v[6:]
            count = 0
            while count < len(v) and v[count] != ';':
                count += 1
            j = v[: count]
            v = v[count:]
            #print('\t' + j)
            newpath = os.path.join(path, "toxins.txt")
            #print(newpath)
            if os.path.isfile(newpath):
                file = open(newpath, "a")
            else:
                file = open(newpath, "w+")
            file.write("toxin:" + j + " ")
            file.close()
            continue
        if v.startswith("symptom="):
            v = v[8:]
            count = 0
            while count < len(v) and v[count] != ';':
                count += 1
            j = v[: count]
            v = v[count:]
            #print('\t' + j)
            newpath = os.path.join(path, "symptoms.txt")
            #print(newpath)
            if os.path.isfile(newpath):
                file = open(newpath, "a")
            else:
                file = open(newpath, "w+")
            file.write("symptom:" + j + " ")
            file.close()
            continue
        else:
            v = v[1:]
            continue

def massDownload():
    downloadPMID()
    #downloadURL()

def downloadPMID():
    for file in os.listdir(constants.newdir):
        if not file.endswith('.csv'):
            foldername = os.path.join(constants.newdir, file)
            pathname = os.path.join(foldername, 'PMID.txt')
            print(pathname)
            if os.path.isfile(pathname):
                    with open(pathname, 'r', encoding='utf-8') as f:
                            r = requests.get(f.read())
                            with open(os.path.join(foldername, 'pubmedAbstract.txt'), 'w+', encoding='utf-8') as newfile:
                                newfile.write(r.text)
                                print('success')
            else:
                print('path does not exist')



# def downloadURL():
#     for file in os.listdir(constants.newdir):
#         if not file.endswith('.csv'):
#             foldername = os.path.join(constants.newdir, file)
#             pathname = os.path.join(foldername, 'url.txt')
#             print(pathname)
#             if os.path.isfile(pathname):
#                 with open(pathname, 'r', encoding='utf-8') as f:
#                     for url in f:
#                         print(url)
#                         try:
#                             response = requests.get(url)
#                         except:
#                             print('failed to get response...')
#                             continue
#                         filename = os.path.join(os.path.join(constants.newdir, file), 'URL_')
#                         i = '0'
#                         while os.path.isfile(filename + i):
#                             i+=1
#                         filename = filename + i
#
#                         if url.endswith('.pdf\n') and isinstance(response.content.decode(), str):
#                             filename = filename + i + '.pdf'
#                             with open(filename, 'w', encoding='utf-8') as pdfFile:
#                                 pdfFile.write(response.content.decode('utf-8'))
#                                 print('successpdf')
#                         else:
#                             filename = filename + i + '.txt'
#                             soup = BeautifulSoup(url,'html.parser')
#                             for anchor in soup.find_all('a'):
#                                 print(anchor.get('href', '/'))
#                                 with open(filename, 'a', encoding='utf-8') as newfile:
#                                     newfile.write(anchor.get('href', '/'))
#                             print('successtxt')
#             else:
#                 print('path does not exist')


# def separateDOI():
#     numAbstracts = 0
#     numDOI = 0
#     for file in os.listdir(constants.newdir):
#         f = os.path.join(newdir, file)
#         fileName = os.path.join(f, "pubmedAbstract.txt")
#         if os.path.isfile(fileName):
#             PMIDfile = open(fileName, 'r')
#             for url in PMIDfile:
#                 if url.startswith('DOI: '):
#                     doi = url[5:-2]
#                     doi.replace('/', '_')
def checkReference(s, filename):
    threshold = 0
    reference = 0
    for w in s.split(" "):
        for name in filename.split(' '):
            if(len(name) == len(w)):
                if dist.hamming(w, name) > threshold:
                    reference += 1
    print(filename + ' references: ' + str(reference))




def finishedStats():
    numPathogens = 0
    numDOI = 0
    numPMID = 0
    for file in os.listdir(constants.newdir):
        filename = file.replace('_', ' ')
        filename = filename.replace(';', ':')
        filename = filename.replace('!', '?')
        filename = filename.replace('-', '/')
        if not file.endswith('.csv'):
            numPathogens += 1
            for innerFile in os.listdir(os.path.join(constants.newdir, file)):
                if innerFile.startswith('DOI'):
                    numDOI += 1
                elif(innerFile.startswith('pubmed')):
                    f = open(os.path.join(os.path.join(constants.newdir, file), 'pubmedAbstract.txt'), 'r', encoding= 'utf-8')
                    i = 1
                    s = ''
                    for line in f:
                        if(line.startswith(str(i) + '. ')):
                            if line.startswith('PMID: '):
                                s = ''
                            while not line.startswith('PMID: '):
                                s += line
                                break
                            checkReference(s, filename)
                            i+=1
                            numPMID += 1

    print("Pathogens: " + str(numPathogens))
    print("DOI: " + str(numDOI))
    print("Abstracts: " + str(numPMID))




def main():
    #reformat()
    #appendSuffixes()
    #massDownload()
    finishedStats()




if __name__=="__main__":
    main()

