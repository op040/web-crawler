from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time

import nltk # imported 
from nltk.corpus import stopwords # imported 
from nltk.tokenize import word_tokenize # imported 
from utils import get_urlhash, normalize # imported 
from bs4 import BeautifulSoup   # imported
import re # imported 
from scuffedTokenizer import tokenizeText 

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)
        
    def run(self):
        
        while True:

            tbd_url = self.frontier.get_tbd_url()

            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                with open("dataReport.txt", "a") as text_file:
                    text_file.write(f"Number of Unique Pages: {self.frontier.numUniquePages}\n")
                    text_file.write(f"Longest Page in term of word count: {self.frontier.current_longest_page[0]} word count: {self.frontier.current_longest_page[1]}\n")
                    text_file.write(f"50 most common words: {sorted(self.frontier.word_dictionary.items(), key = lambda key: key[1], reverse = True)[0:50]}\n")
                    text_file.write(f"Number of Unique Sub-Domains: {self.frontier.numUniqueSubDomains} Unique Sub-Domains: {sorted(self.frontier.uniqueSubDomains.items(), key = lambda key: key[0], reverse = False)}\n")
                break
            resp = download(tbd_url, self.config, self.logger)
 
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.") #{self.frontier.to_be_downloaded}
            
            scraped_urls = scraper(tbd_url, resp, self.frontier.fingerprintList)

            for scraped_url in scraped_urls:
  
                self.frontier.add_url(scraped_url)
                
            try:
                
                # url = normalize(tbd_url)
                # urlhash = get_urlhash(url)

                if ((resp.raw_response != None) and (resp.status > 199) and (resp.status < 400) 
                    and (resp.raw_response.content != "") and ("Content-Type" in resp.raw_response.headers) and re.match(r"^text/html((;.*)|$)", resp.raw_response.headers['Content-Type'])):
                    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
                    
                    tokens = tokenizeText(soup.get_text()) # stop words included

                    for token in tokens:
                        if (token.isnumeric() == False):
                            if (token not in self.frontier.word_dictionary):
                                self.frontier.word_dictionary[token] = 1
                            else:
                                self.frontier.word_dictionary[token] =  self.frontier.word_dictionary[token] + 1
                    
                    if (self.frontier.current_longest_page == None):
                        self.frontier.current_longest_page = [tbd_url, len(tokens)]
                    elif (len(tokens) > self.frontier.current_longest_page[1]):
                        self.frontier.current_longest_page[0] = tbd_url
                        self.frontier.current_longest_page[1] = len(tokens)

                    # Finding Unique subdomains 
                    matchObject = re.match(r"^.+//(.+\.ics\.uci\.edu)((\/.*)|$)", tbd_url)
                    if (matchObject != None):
                        if (matchObject.group(1) not in self.frontier.uniqueSubDomains):                    
                            self.frontier.uniqueSubDomains[matchObject.group(1)] = 1
                            self.frontier.numUniqueSubDomains = self.frontier.numUniqueSubDomains + 1
                        else:
                            self.frontier.uniqueSubDomains[matchObject.group(1)] += 1
            except:
                pass
            
            # marking current urls as complete / crawling is finished on this url
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

        # Logging number of unique pages, longest page in term of word count , 50 most common words,
        # number of unique sub-domains.