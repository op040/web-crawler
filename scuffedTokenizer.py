import re
import hashlib
from bs4 import BeautifulSoup   # i imported
import requests                 # i imported
from nltk.corpus import stopwords # imported 
from collections import defaultdict

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
    tokenList = (re.split(r"\n+|_+|[^a-zA-Z0-9'-]+",textString))
    eng_stopwords = set(stopwords.words("english"))
    return [word for word in tokenList if ((not word in eng_stopwords) and (len(word) > 1))]

def computeWordFrequencies(tokenList):
    tokenMap = defaultdict(int)
    for token in tokenList:
        if (token != ""):
            tokenMap[token] += 1

    return tokenMap

def compute_Text_Fingerprint(text):
    tokensList = tokenizeText(text)
    frequencyDict = computeWordFrequencies(tokensList)
    return getFingerPrint(frequencyDict)
    
