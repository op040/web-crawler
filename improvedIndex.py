import os
import pickle
import gc
import json
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from allWordsTokenizer import tokenizeText, computeWordFrequencies
import re
from collections import defaultdict
# import ujson as json
import time
import math

def parseDocumentStorage(path):
    total_docs = countTokens(path)
    third_docs = int(countTokens(path)/3)
    idCounter = 0
    tokenCount = 0
    portStem = PorterStemmer()
    file_num = 1
    id_to_url = {}
    token_to_postings = defaultdict(list)

    for root, directoryList, fileList in os.walk(path, topdown=False):
        for file_name in fileList:
            pathName = os.path.join(root, file_name)

            idCounter = idCounter + 1
            
            print(idCounter,pathName)

            fileDataDictionary = {}
            with open(pathName, "r") as openedFile:
                fileDataDictionary = json.load(openedFile)
            
            id_to_url[idCounter] = fileDataDictionary["url"]
            
            fileSoup = BeautifulSoup(fileDataDictionary["content"], "html.parser")
            textualContent = fileSoup.get_text()
           
            #sdadasda

            impSet = set()
            for b in fileSoup.find_all(["b", "strong", "h1", "h2", "h3", "title"]):
                bTextList = tokenizeText(b.text)
                for impTerm in bTextList:
                    impTermStem = portStem.stem(impTerm)
                    impSet.add(impTermStem)

            #sdadasdas

            tokenList = tokenizeText(textualContent)
            tokenFrequencyDict = computeWordFrequencies(tokenList)
            for termStem in tokenFrequencyDict: 
                # tokenCount = tokenCount + 1
                impMultiplier = 1
                if(termStem in impSet):
                    print("inside ", termStem)
                    impMultiplier = 1.5
                termTf = 1 + math.log(tokenFrequencyDict[termStem] * impMultiplier, 10)
                token_to_postings[termStem].append( [idCounter, termTf] )
            
                
            if(idCounter == third_docs or idCounter == third_docs*2 or idCounter==total_docs):
                with open(str(file_num) + ".txt", "w", newline='\n') as file_one: 
                    ind_of_ind = {}
                    for k,v in sorted(token_to_postings.items(), key = lambda x: x[0]):
                        ind_of_ind[k] = file_one.tell()
                        output = json.dumps(v) + "\n"
                        file_one.write(output)
                    with open(str(file_num)+"ind.txt","w") as file_1:
                        json.dump(ind_of_ind,file_1)
                file_num += 1
                token_to_postings.clear()

        with open("urls.txt", "w", newline='\n') as url_file:
            json.dump(id_to_url,url_file)
            
def mergeTwoFiles(file1, file1_ind, file2, file2_ind, new_file, new_file_ind):
    firstOpenedFile = open(file1_ind, "r")
    secondOpenedFile = open(file2_ind,"r")
    dataFile1 = open(file1, "r", newline='\n')
    dataFile2 = open(file2, "r", newline='\n')
    index_one = json.load(firstOpenedFile)
    index_two = json.load(secondOpenedFile)
    index_one_keys = list(index_one.keys())
    index_two_keys = list(index_two.keys())
    index1 = 0
    index2 = 0
    ind_of_ind = {}
    mergedFile = open(new_file,"w",newline = '\n')
    mergedFile_ind = open(new_file_ind,"w")
    while ( (index1 < len(index_one_keys)) or (index2 < len(index_two_keys)) ):
        if(index1==len(index_one_keys)):
            while(index2!=len(index_two_keys)):
                #append everything in index2 to new file
                offset2 = index_two[index_two_keys[index2]] 
                dataFile2.seek(offset2)
                list2 = json.loads(dataFile2.readline()) # postings lists1
                
                if(new_file == "finalmerge.txt"):
                    idf = math.log( (55393.0 / len(list2)) , 10)
                    for element in list2:
                        element[1] = element[1] * idf

                ind_of_ind[index_two_keys[index2]] = mergedFile.tell() 
                list2 = json.dumps(list2) + "\n"
                mergedFile.write(list2)
                index2 += 1
        elif(index2==len(index_two_keys)):
            while(index1!=len(index_one_keys)):
                #append everything in index1 to new file
                offset1 = index_one[index_one_keys[index1]] 
                dataFile1.seek(offset1)
                list1 = json.loads(dataFile1.readline()) # postings lists1

                if(new_file == "finalmerge.txt"):
                    idf = math.log( (55393.0 / len(list1)) , 10)
                    for element in list1:
                        element[1] = element[1] * idf

                ind_of_ind[index_one_keys[index1]] = mergedFile.tell() 
                list1 = json.dumps(list1) + "\n"
                mergedFile.write(list1)
                index1 += 1
        else:
            if(index_one_keys[index1]==index_two_keys[index2]):
                offset1 = index_one[index_one_keys[index1]] 
                offset2 = index_two[index_two_keys[index2]]
                dataFile1.seek(offset1)

                list1 = json.loads(dataFile1.readline()) # postings lists1
                dataFile2.seek(offset2)
                list2 = json.loads(dataFile2.readline()) # postings lists2
                list1.extend(list2)                                   # merge and save into list1 

                if(new_file == "finalmerge.txt"):
                    idf = math.log( (55393.0 / len(list1)) , 10)
                    for element in list1:
                        element[1] = element[1] * idf

                ind_of_ind[index_one_keys[index1]] = mergedFile.tell() 
                list1 = json.dumps(list1) + "\n"
                mergedFile.write(list1)                                 # write to a "new file"
                index1 += 1
                index2 += 1
                # merge the posting list of the two keys and save it in the first list
            elif index_one_keys[index1] < index_two_keys[index2]:
                # don't append because it is already in the first list 
                # only add index_one_keys[index1] to the "new file"
                # increment index1
                offset1 = index_one[index_one_keys[index1]] 
                dataFile1.seek(offset1)
                list1 = json.loads(dataFile1.readline()) # postings lists1
                
                if(new_file == "finalmerge.txt"):
                    idf = math.log( (55393.0 / len(list1)) , 10)
                    for element in list1:
                        element[1] = element[1] * idf

                ind_of_ind[index_one_keys[index1]] = mergedFile.tell() 
                list1 = json.dumps(list1) + "\n"
                mergedFile.write(list1)
                index1 += 1
            elif index_one_keys[index1] > index_two_keys[index2]:
                # append index_two_keys[index2] to list 1
                # increment index2
                offset2 = index_two[index_two_keys[index2]] 
                dataFile2.seek(offset2)
                list2 = json.loads(dataFile2.readline()) # postings lists1

                if(new_file == "finalmerge.txt"):
                    idf = math.log( (55393.0 / len(list2)) , 10)
                    for element in list2:
                        element[1] = element[1] * idf

                ind_of_ind[index_two_keys[index2]] = mergedFile.tell() 
                list2 = json.dumps(list2) + "\n"
                mergedFile.write(list2)
                index2 += 1
    json.dump(ind_of_ind,mergedFile_ind)
    firstOpenedFile.close()
    secondOpenedFile.close()
    mergedFile.close()
    mergedFile_ind.close()

# def combineTfIdf(path):

#     for root, directoryList, fileList in os.walk(path, topdown=False):
#         for file_name in fileList:
#             pathName = os.path.join(root, file_name)

#             openedFile = open(pathName, 'rb+')      
#             db = pickle.load(openedFile)

#             for dbIndex in range(len(db)):
#                 db[dbIndex][1] = db[dbIndex][1] * math.log(55393.0/len(db))


#             openedFile.seek(0)
#             pickle.dump(db, openedFile)
#             openedFile.close()

def countTokens(path):
    counter = 0
    for root, directoryList, fileList in os.walk(path, topdown=False):
        for file_name in fileList:
            counter+=1
    return counter

if __name__ == '__main__':
    parseDocumentStorage("DEV")
    # with open("3ind.txt", "r") as checkFile:
    #     indexOfIndex = json.load(checkFile)

    #     with open("3.txt", "r", newline='\n') as dataFile:
    #         for term in indexOfIndex:
    #             dataFile.seek(indexOfIndex[term])
    #             line = dataFile.readline()
    #             print(term, line, end = "")
    # with open("urls.txt", "r") as checkFile:
    #     urls = json.load(checkFile)
    #     for docid,url in urls.items():
    #         print(docid,url,type(docid))
    mergeTwoFiles("1.txt","1ind.txt","2.txt","2ind.txt","merged.txt","mergedind.txt")
    mergeTwoFiles("merged.txt","mergedind.txt","3.txt","3ind.txt","finalmerge.txt","finalmergedind.txt")
    
