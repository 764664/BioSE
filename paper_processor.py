from lxml import etree
import requests
import subprocess
import re
import logging
import sys
from db import *
from sklearn import svm
from sklearn import gaussian_process
import pickle
import math


class PaperProcessor:
    def __init__(self, keyword, num_of_documents=10000):
        print(keyword)
        logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s')
        if keyword:
            self.keyword = keyword
            self.num_of_documents = num_of_documents
            self.papers = {}
            self.failure_pubmed = 0
            self.papers_array = []

            self.get_pubmed()

            self.get_google_scholar()
            # self.truncate_for_display()
            self.add_missing_info()
            self.find_exact_match()
            # self.ranking()
            self.generate_papers_array()
            self.num_papers = len(self.papers_array)

    def basic_search(self, string):
        url = ("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
               "db=pubmed&term=" + string + "&sort=relevance")
        r = requests.get(url)
        root = etree.fromstring(r.content)
        return " ".join([i.text for i in root[3]])

    def get_webenv(self):
        url = ("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
               "db=pubmed&term=" + self.keyword + "&usehistory=y&sort=relevance")
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
            sys.exit("Error in Getting WebEnv.")
            return False
        except IndexError as e:
            logging.warning(e)
            logging.warning("Error in Getting WebEnv.")
            logging.warning("Response is {}".format(r.content))
            sys.exit("Error in Getting WebEnv.")
            return False
        return root[4].text

    def get_pubmed(self):
        logging.info("Started Fetching PubMed.")
        webenv = self.get_webenv()
        if webenv:
            url = (
                "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
                "db=pubmed&retmax=" + str(self.num_of_documents) +
                "&query_key=1&WebEnv=" + webenv)
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

    def get_google_scholar(self):
        logging.info("Started fetching Google Scholar.")
        papers_local = []
        with subprocess.Popen(
            (
                "python3", "scholar.py", "-c", "20", "-A",
                self.keyword + " bioinformatics", "--csv-header"),
            stdout=subprocess.PIPE
            ) as proc, \
            subprocess.Popen((
                "python3", "scholar.py", "-c", "20", "-A",
                self.keyword + " bioinformatics", "--citation", "bt"),
                stdout=subprocess.PIPE) as proc2:
            s = proc.stdout.read()
            sbt = proc2.stdout.read()
            logging.info("len(s) = {}".format(len(s)))
            logging.info("len(sbt) = {}".format(len(sbt)))
            logging.info("Finished fetching Google Scholar.")
            score = 1
            header = {}
            for idx, item in enumerate(map(str.rstrip,
                                       s.decode().split("\n"))):
                if idx == 0:
                    for idx2, word in enumerate(item.split("|")):
                        if word == "title":
                            header["Title"] = idx2
                        if word == "num_citations":
                            header["Citations"] = idx2
                        if word == "url":
                            header["URL"] = idx2
                        if word == "year":
                            header["PubDate"] = idx2
                        if word == "url_citations":
                            header["Citations_URL"] = idx2
                else:
                    if item:
                        one_item = {}
                        splited = item.split("|")
                        if "Title" in header:
                            one_item["Title"] = splited[header["Title"]]
                        if "URL" in header:
                            one_item["URL"] = splited[header["URL"]]
                            if not one_item["URL"] or \
                                    one_item["URL"] == "None":
                                continue
                        if "PubDate" in header:
                            one_item["PubDate"] = splited[header["PubDate"]]
                            one_item["Year"] = one_item["PubDate"]
                        one_item["Score"] = score
                        if "Citations" in header:
                            one_item["Citations"] = \
                                splited[header["Citations"]]
                        if "Citations_URL" in header:
                            one_item["Citations_URL"] = \
                                splited[header["Citations_URL"]]
                        one_item["Journal"] = ""
                        one_item["Author"] = ""
                        score = score - 1 / self.num_of_documents
                        papers_local.append(one_item)
            for item in sbt.decode().split("b'"):
                m = re.match(
                    r'.+title\=\{(.+)\}.+author\=\{(.+)\}.+'
                    'journal\=\{(.+?)\}', item, re.DOTALL)
                if m:
                    for added_item in papers_local:
                        if m.group(1) == added_item["Title"]:
                            if m.group(2):
                                added_item["Author"] = m.group(2)
                            if m.group(3):
                                added_item["Journal"] = m.group(3)
        for paper in papers_local:
            if paper["Title"] in self.papers:
                self.papers[paper["Title"]]["Score"] = (self.papers[paper["Title"]]["Score"] + paper["Score"]) / \
                                                       math.sqrt(1+self.papers[paper["Title"]]["Score"] * paper["Score"])
                self.papers[paper["Title"]]["Citations"] = paper["Citations"]
                self.papers[paper["Title"]]["Citations_URL"] = \
                    paper["Citations_URL"]
            else:
                if not paper["Author"]:
                    paper["Author"] = "Failed to fetch author names."
                # self.papers[paper["Title"]] = paper
        logging.info("Fetched {} papers from Google Scholar".format(
            len(papers_local)))

    def find_exact_match(self):
        for title, paper in self.papers.items():
            try:
                if ":" in paper["Title"]:
                    # Keyword is in title
                    if self.keyword.lower() in \
                            paper["Title"].split(":")[0].lower():
                        paper["Score"] += 1
                        # Keyword equals to title
                        if paper["Title"].split(":")[0].lower().rstrip() == \
                                self.keyword.lower():
                            paper["Score"] += 2
            except Exception as e:
                logging.warning("Error in Finding Exact Match.")
                logging.warning(e)

    def truncate_for_display(self):
        for title, paper in self.papers.items():
            if(len(paper["Author"]) > 100):
                paper["Author"] = paper["Author"].split(", ")[0] + \
                    ", ... , " + paper["Author"].split(", ")[-1]
            if(len(paper["Title"]) > 100):
                paper["Title"] = paper["Title"][:100] + "..."

    def generate_papers_array(self):
        self.papers_array = list(self.papers.values())
        logging.info("Have {} papers in total.".format(len(self.papers_array)))
        self.papers_array.sort(key=lambda x: x["Score"])
        self.papers_array.reverse()
        for index, paper in enumerate(self.papers_array):
            paper["ID"] = index

    def add_missing_info(self):
        self.add_journal_if()

    def add_journal_if(self):
        for k,v in self.papers.items():
            if 'Journal' not in v or not v['Journal']:
                v["Journal_IF"] = 0
                continue
            try:
                stripped_journal_name = re.sub('[\W_]+', '', v["Journal"].upper())
                v["Journal_IF"] = Journal.get(Journal.title==stripped_journal_name).impact_factor
            except DoesNotExist:
                try:
                    if len(stripped_journal_name) >= 12:
                        v["Journal_IF"] = Journal.get(Journal.title.startswith(stripped_journal_name[:12])).impact_factor
                    elif len(stripped_journal_name) >= 8:
                        v["Journal_IF"] = Journal.get(Journal.title.startswith(stripped_journal_name[:8])).impact_factor
                    elif len(stripped_journal_name) >= 4:
                        v["Journal_IF"] = Journal.get(Journal.title.startswith(stripped_journal_name[:4])).impact_factor
                    else:
                        v["Journal_IF"] = 0
                except DoesNotExist:
                    v["Journal_IF"] = 0


    def ranking(self):
        model = self.check_model()
        if model:
            clf = model[0]
            number_clicks = model[1]
            maximum_ml_score = -1
            for k,v in self.papers.items():
                if "Journal_IF" in v and "Year" in v:
                    x = [[v["Year"], v["Journal_IF"]]]
                    score_ml = clf.predict(x)[0]
                    v["Score_ML"] = score_ml
                    if score_ml > maximum_ml_score:
                        maximum_ml_score = score_ml
                    weight = 1 - math.pow(0.5, 0.1*number_clicks)
                    v["Weight"] = weight
            for k,v in self.papers.items():
                if "Score_ML" in v:
                    v["Score_ML"] *= 1 / maximum_ml_score
                    # logging.debug("{}: {}".format(v["Title"], v["Score_ML"]))
                    v["Score"] = v["Score"]*(1-v["Weight"]) + v["Score_ML"]*v["Weight"]
        else:
            pass

    def check_model(self):
        ALWAYS_CREATE_NEW_MODEL_AND_DONT_SAVE = True
        if ALWAYS_CREATE_NEW_MODEL_AND_DONT_SAVE:
            new_model = self.train_model()
            return new_model
        try:
            search_term = SearchTerm.get(SearchTerm.keyword == self.keyword)
            model = Model.get(Model.search_term == search_term)
            if datetime.datetime.now() - model.last_modified > datetime.timedelta(days = 1):
                new_model = self.train_model()
                if new_model:
                    model.model = pickle.dumps(new_model)
                    model.last_modified = datetime.datetime.now()
                    model.save()
                return new_model
            else:
                return pickle.loads(model.model)
        except DoesNotExist:
            new_model = self.train_model()
            if new_model:
                Model.create(
                    search_term = SearchTerm.get(SearchTerm.keyword == self.keyword),
                    model = pickle.dumps(new_model)
                )
            return new_model

    def train_model(self):
        x, y = [], []
        #clicks = SearchTerm.get(SearchTerm.keyword == self.keyword).clicks
        clicks = Click.select(Paper, Click).join(Paper).switch(Click).join(SearchTerm).where(SearchTerm.keyword == self.keyword)
        if clicks.count() == 0:
            return False
        for click in clicks:
            x.append(
                [
                    click.paper.year,
                    click.paper.journal_if
                ]
            )
            y.append(click.click_count)
        #clf = svm.SVR(kernel="rbf")
        #clf.fit(x, y)
        #return [clf, sum(y)]
        gp = gaussian_process.GaussianProcess(theta0=1e-2, thetaL=1e-4, thetaU=1e-1)
        gp.fit(x, y)
        return [gp, sum(y)]