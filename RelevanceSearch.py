import sys
import os
import pickle
from nltk.stem import PorterStemmer
import time
import json
from collections import defaultdict


def runSearchEngine():
    merged_ind = open("finalmergedind.txt", "r")
    idByteOffset = json.load(merged_ind)
    merged_txt = open("finalmerge.txt","r")
    portStem = PorterStemmer()
    urls = open("urls.txt","r")
    urls_map = json.load(urls)
    while(True):
        # Strip the user input
        userInput = input("Input Search: ").strip()
        start = time.time()
        # Split the user input on space char 
        search_words = set(userInput.split(" "))
    
        list_search = []

        for word in search_words:
            wordStem = portStem.stem(word)
            # If the word is in the index - 
            if(wordStem in idByteOffset):
                # Get the offset of the word in the index 
                offset = idByteOffset[wordStem]
                # Seek to the doc id's of the word in index 
                merged_txt.seek(offset)
                # Load the postingList of the word
                postingList = json.loads(merged_txt.readline()) 
                # Append the posting list to the list
                list_search.append(postingList)

        if(len(list_search) != 0): 
            results = searchProcess(list_search, urls_map)
            end = time.time()
            if(results == None):
                print("No Results Found")
            else:
                print(results)
                print(end - start)
        else:
            print("No Results Found")

    # merged_ind = open("finalmergedind.txt", "r")
    # idByteOffset = json.load(merged_ind)
    # merged_txt = open("finalmerge.txt","r")
    # portStem = PorterStemmer()
    # urls = open("urls.txt","r")
    # urls_map = json.load(urls)
    # while(True):
    #     userInput = input("Input Search: ").strip()
    #     search_words = userInput.split(" ")
    #     list_search = []
    #     for word in search_words:
    #         wordStem = portStem.stem(word)
    #         offset = idByteOffset[wordStem]
    #         merged_txt.seek(offset)
    #         postingList = json.loads(merged_txt.readline()) 
    #         list_search.append(postingList)
            
    #     print(searchProcess(list_search, urls_map))
    #         merged_txt.seek(offset)
    #         postingList = json.loads(merged_txt.readline()) 
    #         list_search.append(postingList)
            
    #     print(searchProcess(list_search, urls_map))

def searchProcess(inputPostingList, urls_map):
    wordPostings = inputPostingList
    foundIds = []

    scores = defaultdict(int)
    length = {}

    url_links = ""

    if (len(wordPostings) == 1):
        for element in wordPostings[0]:
            scores[element[0]] += element[1]
        
    else:
        wordPostings = sorted(wordPostings, key = lambda x : len(x))

        for queryTermList in wordPostings:
            for documentData in queryTermList:
                scores[documentData[0]] += documentData[1]
            
    top10 = sorted(scores.items(), key = lambda y : y[1], reverse = True)
    top10 = top10[:10]

    # copy apsted
    for num in range(0,len(top10)):
        # print(urls[i])
        line = urls_map[str(top10[num][0])]
        url_links += line + "\n"
    
    return url_links

if __name__ == '__main__':

    runSearchEngine()
