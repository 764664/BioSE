import logging
import requests
from lxml import etree
import re
import json
from IPython import embed

class PubMedFetcher:
    def __init__(self, keyword, num_of_documents=2):
        self.keyword = keyword
        self.num_of_documents = num_of_documents
        self.papers = {}
        self.error = False

        idlist = self.get_idlist()
        self.fetch_from_idlist(idlist)

    def get_webenv(self):
        logging.info("Getting WebEnv.")
        url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
               "db=pubmed&term={}&usehistory=y&sort=relevance".format(self.keyword))
        logging.debug(url)
        r = requests.get(url)
        root = etree.fromstring(r.content)
        try:
            assert root[4].tag == "WebEnv" and root[3].text == "1"
        except AssertionError as e:
            logging.warning("Error in Getting WebEnv.")
            logging.warning("Response is {}".format(r.content))
            logging.warning(root[4].tag)
            logging.warning(root[3].text)
            self.error = "Error in Getting WebEnv."
            return False
        except IndexError as e:
            logging.warning(e)
            logging.warning("Error in Getting WebEnv.")
            logging.warning("Response is {}".format(r.content))
            self.error = "Error in Getting WebEnv."
            return False
        return root[4].text

    def get_idlist(self):
        logging.info("Getting WebEnv.")
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        payload = {
            'db': 'pubmed',
            'sort': 'relevance',
            'term': self.keyword,
            'retmode': 'json',
            'retmax': self.num_of_documents
        }
        logging.debug(url)
        req = requests.post(url, data=payload)
        j = req.json()
        idlist = j['esearchresult']['idlist']
        return idlist

    def fetch_from_idlist(self, idlist):
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        payload = {
            'id': ','.join(list(map(lambda x: str(x), idlist))),
            'db': 'pubmed',
            'retmax': len(idlist)
        }
        logging.debug(url)
        r = requests.post(url, data=payload)
        score = 1
        ranking = 1
        count = 0
        logging.info("Start parsing.")

        for item in r.text.split("Pubmed-entry"):
            paper = self.process_one(item)
            if paper:
                paper["Score"] = score
                paper["Ranking"] = ranking
                self.papers[paper["Title"]] = paper
                score = score - 1 / self.num_of_documents
                ranking += 1
                count += 1
        logging.info("Got %d papers from %d entries", count, self.num_of_documents)

    def process_one(self, item):
        if len(item) < 30:
            return None
        m = re.search("pmid (\d+).+?title.+?name \"(.+?)\".+?authors \{(.+?)\},\s*from journal.+?name \"(.+?)\".+?year (\d+).+?month (\d+).+?abstract \"(.+?)\"", item, re.DOTALL)
        error_count = 1
        if m:
            id = m.group(1)
            title = m.group(2).replace("\n", "").strip()
            author = m.group(3)
            m_author = re.findall("name ml \"(.+?)\"", author)
            journal = m.group(4)
            year = m.group(5)
            month = m.group(6)
            abstract = m.group(7).replace("\n", "").strip()
            h = {
                "Source": "PubMed",
                "PMID": id,
                "Title": title,
                "Author": m_author,
                "Journal": journal,
                "Year": int(year),
                "Abstract": abstract
            }
            h["URL"] = "http://www.ncbi.nlm.nih.gov/pubmed/" + h["PMID"]
            return h
        else:
            logging.warning("Parse error. #%d", error_count)
            error_count += 1
            return None


    def process(self):
        url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmax={}&query_key=1&WebEnv={}"
                .format(str(self.num_of_documents), self.webenv))
        logging.debug(url)
        r = requests.get(url)
        # print(r.content)
        score = 1
        ranking = 1
        count = 0
        logging.info("Start parsing.")

        for item in r.text.split("Pubmed-entry"):
            paper = self.process_one(item)
            if paper:
                paper["Score"] = score
                paper["Ranking"] = ranking
                self.papers[paper["Title"]] = paper
                score = score - 1 / self.num_of_documents
                ranking += 1
                count += 1
        logging.info("Got %d papers from %d entries", count, self.num_of_documents)

    def get_pubmed(self):
        logging.info("Started Fetching PubMed.")
        if self.webenv:
            url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
                "db=pubmed&retmax=" + str(self.num_of_documents) +
                "&query_key=1&WebEnv=" + self.webenv)
            logging.debug(url)
            r = requests.get(url)
            root = etree.fromstring(r.content)
            if root[0].tag == "ERROR":
                logging.warning(root[0].text)
                self.failure_pubmed = 1
                return
            score = 1
            ranking = 1
            for item in root:
                one_item = {}
                one_item["Source"] = "PubMed"
                one_item["PMID"] = item[0].text
                one_item["URL"] = "http://www.ncbi.nlm.nih.gov/pubmed/" + \
                                  one_item["PMID"]
                for i in item:
                    if "Name" in i.attrib:
                        if i.attrib["Name"] == "Title":
                            if not i.text:
                                continue
                            one_item["Title"] = i.text.rstrip(".")
                        if i.attrib["Name"] == "PubDate":
                            one_item["PubDate"] = i.text
                            try:
                                one_item["Year"] = int(i.text[:4])
                            except Exception:
                                one_item["Year"] = 2000
                        if i.attrib["Name"] == "FullJournalName":
                            one_item["Journal"] = i.text
                        if i.attrib["Name"] == "LastAuthor":
                            one_item["LastAuthor"] = i.text
                        if i.attrib["Name"] == "AuthorList":
                            author_list = []
                            for author in i:
                                author_list.append(author.text)
                            one_item["Author"] = ", ".join(author_list)
                one_item["Score"] = score
                one_item["PubMedRanking"] = ranking
                score = score - 1 / self.num_of_documents
                ranking += 1
                if "Title" in one_item and "Author" in one_item:
                    self.papers[one_item["Title"]] = one_item
            logging.info("Finished Fetching PubMed.")
            logging.info("Fetched {} papers from PubMed.".format(len(root)))
        else:
            self.failure_pubmed = 1

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')
    p = PubMedFetcher("methylation", num_of_documents=100)
    for paper in p.papers.values():
        if paper["Ranking"] < 2:
            print(paper)