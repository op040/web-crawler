import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup   # i imported
import requests                 # i imported
#import faster_than_requests as requests
import hashlib
from utils import get_urlhash, normalize # imported 
from nltk.corpus import stopwords # imported 
from nltk.tokenize import word_tokenize
from scuffedTokenizer import * 

def scraper(url, resp, listOfFingerprints):

    scrappedLinks = []
    goodUrl = True


    if ((resp.raw_response == None) or (resp.status < 200) or (resp.status > 399) or (resp.raw_response.content == "")):

        goodUrl = False
    if(goodUrl):

        contentType = ""
        if ("Content-Type" in resp.raw_response.headers):
            contentType = resp.raw_response.headers["Content-Type"]
        if (not re.match("^text/html((;.*)|$)", contentType)):
      
            goodUrl = False
        else:
 
            preCheckSoup = BeautifulSoup(resp.raw_response.content, "html.parser")
            preCheckSoupText = preCheckSoup.get_text()

            tokensList = tokenizeText(preCheckSoupText)
            if((len(tokensList) < 200) or (len(tokensList) > 40000)):
                return []
            frequencyDict = computeWordFrequencies(tokensList)
            preCheckFingerPrint = getFingerPrint(frequencyDict)
            for index in range(len(listOfFingerprints) - 1, -1, -1):
                
                if(preCheckFingerPrint in listOfFingerprints):
                    goodUrl = False
                    break
                if(compute_similarity(preCheckFingerPrint, listOfFingerprints[index]) > .85):
                    goodUrl = False
                    break
    
    if (goodUrl == True):
        listOfFingerprints.append(compute_Text_Fingerprint(preCheckSoupText))

        scrappedLinks = extract_next_links(url, resp)
                                                                

    return scrappedLinks

def extract_next_links(url, resp):
    # Implementation requred.
    #    print("******* extract_next_link ***********")

    url = url.strip() # whitespace at end of link example: "http://www.ics.uci.edu/~mlevorat/ " scrapped from "https://www.ics.uci.edu/faculty/profiles/view_faculty.php?ucinetid=levorato"

    l = []
    try:
        if ((resp.status < 200) or (resp.status > 399) or (resp.raw_response == None) or (resp.raw_response.content == "")):
            pass
        else:
            soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
            url_parsed = urlparse(url)

            for link in soup.find_all('a', href = True):
                parsed = urlparse((link['href'].split("#"))[0])
                
                link = (link['href'].split("#"))[0]

                if (parsed.scheme == "" and parsed.netloc == "" and len(parsed.path) != 0):
                    #urlParsed = urlparse(url)
                    if (re.match(r"^today\.uci\.edu$", url_parsed.netloc) and not re.match(r"\/department\/information_computer_sciences(\/.+|$)", parsed.path)):
                        pass
                    else:
                        link = urljoin(url, link)
                            # if (url[len(url) - 1] == "/"):
                            #     link = url + parsed.path
                            # else:
                            #     link = url + "/" + parsed.path

                if (is_valid(link)):
                    l.append(link)

    except:
        pass
    return l

def is_valid(url):
    try:

        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False
        if (not (re.match(r"(.+\.ics\.uci\.edu$)|(.+\.cs\.uci\.edu$)|(.+\.informatics\.uci\.edu$)|(.+\.stat\.uci\.edu$)", parsed.netloc)
            or (re.match(r"^today\.uci\.edu$", parsed.netloc) and re.match(r"\/department\/information_computer_sciences(\/.+|$)", parsed.path)))):
            return False

        # url = re.sub("\?|\n", "", url) # . CANNOT DETECT \? and \n example: "http://sli.ics.uci.edu/Classes/2015W-178?action=download&upname=31-markov.pdf"
        # parsed = urlparse(url)
        pathAndQuery = parsed.path
        if ((parsed.query.strip()) != ""):
            if ((len(parsed.path) > 1) and (parsed.path[len(parsed.path) - 1] == "/")):
                pathAndQuery = pathAndQuery + "?" + parsed.query
            else:
                pathAndQuery = pathAndQuery + "/" + "?" + parsed.query
        
        pathAndQuery = re.sub(r"\n", "", pathAndQuery)
        
        # if (re.match(r"^evoke.ics.uci.edu", parsed.netloc) and re.search(r"replytocom=[a-zA-Z0-9]+(\/$|$)", parsed.query)): 
        #     # print("evoke bad")
        #     return False
        
        return not re.match(
            r".*\.(m|scm|bam|patch|war|sql|java|xml|sh|py|css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", pathAndQuery.strip().lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise