import re
import hashlib
#from bs4 import BeautifulSoup   # i imported
#import requests                 # i imported
#from nltk.corpus import stopwords # imported 
from collections import defaultdict
from nltk.stem import PorterStemmer

# portStem = PorterStemmer()

def compute_similarity(fingerprint1, fingerprint2):
    diff_counter = 0
    for bit in range(0, 128):
        if (((fingerprint1 >>  bit) & 1) != ((fingerprint2 >>  bit) & 1)):
            diff_counter = diff_counter + 1 
    return (128 - diff_counter) / 128 

def getFingerPrint(textFrequency):
    tockenBin = {}
    for tocken in textFrequency:
        tockenHash = hashlib.md5(tocken.encode())
        tockenBin[tocken] = int(tockenHash.hexdigest(),16)   
    v = [0]*128
    for i,j in tockenBin.items():
        for a in range(0, 128):
            r = (j >> a) & 1
            if r == 1:
                v[127 - a] += textFrequency[i]
            else:
                v[127 - a] -= textFrequency[i]
    binaryString = ""
    for i in v:
        if i > 0:
            binaryString += "1"
        else:
            binaryString += "0"

    return int(binaryString, 2)

def tokenizeText(textString):
    tokenList = []

    textString = textString.lower()
    tokenList = (re.split(r"\n+|_+|[^a-zA-Z0-9]+",textString))
    #eng_stopwords = set(stopwords.words("english"))
    returnList = []
    for word in tokenList:
        # word = re.sub(r"'|-", "", word).strip(".")
        if (len(word) > 50):
            returnList.append(word[:50])
        elif (len(word) > 1):
            returnList.append(word)
    return returnList
    
def computeWordFrequencies(tokenList):
    portStem = PorterStemmer()

    tokenMap = defaultdict(int)
    for token in tokenList:
        tokenStem = portStem.stem(token)
        if (tokenStem != ""):
            tokenMap[tokenStem] += 1

    return tokenMap

def frequenciesAndPosition(tokenList):
    portStem = PorterStemmer()

    tokenMap = {}
    for num in range(len(tokenList)):
        tokenStem = portStem.stem(tokenList[num])

        if (tokenStem in tokenMap):
            tokenMap[tokenStem][0] += 1
            tokenMap[tokenStem].append(num)
        else:
            tokenMap[tokenStem] = [1, num]
    return tokenMap

def compute_Text_Fingerprint(text):
    tokensList = tokenizeText(text)
    frequencyDict = computeWordFrequencies(tokensList)
    return getFingerPrint(frequencyDict)
    
