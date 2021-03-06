import math
import pickle
import re
import subprocess
import logging

from sklearn import gaussian_process

from src.models.schema import Journal, SearchItem
from src.helpers.pubmed import PubMedFetcher
from src.helpers.vectorize_paper import vectorize_paper
from operator import itemgetter

class PaperProcessor:
    def __init__(self, keyword, num_of_documents=100, postprocessing = True):
        if keyword:
            logging.basicConfig(level=logging.INFO)
            self.keyword = keyword
            self.num_of_documents = num_of_documents
            self.papers = {}
            self.failure_pubmed = 0
            self.papers_array = []

            self.get_pubmed()

            # self.bag = AbstractProcessor(self.papers).bag
            # self.words = [[y, self.bag[y]] for y in sorted(list(self.bag.keys()), key=lambda x: self.bag[x], reverse=True)[:30]]

            if postprocessing:
                self.get_scores()
            # self.get_google_scholar()
            # self.truncate_for_display()
                # self.add_missing_info()
            # self.find_exact_match()
            # self.ranking()
            self.generate_papers_array()
            self.num_papers = len(self.papers_array)

    def get_pubmed(self):
        pubmed = PubMedFetcher(keyword=self.keyword, num_of_documents=self.num_of_documents)
        self.papers = pubmed.papers

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
                self.papers[paper["Title"]] = paper
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
        paper_ids = [paper["DBID"] for title, paper in self.papers.items()]
        search_item = SearchItem.objects(keyword=self.keyword).get()
        search_item.update(add_to_set__papers=paper_ids)
        # self.papers_array = list(self.papers.values())
        # logging.info("Have {} papers in total.".format(len(self.papers_array)))
        # self.papers_array.sort(key=lambda x: x["Score"])
        # self.papers_array.reverse()
        # for index, paper in enumerate(self.papers_array):
        #     paper["ID"] = index
        search_item.reload()
        self.papers_array = self.get_scores()
        if not self.papers_array:
            self.papers_array = search_item.papers

    def get_scores(self):
        try:
            item = SearchItem.objects(keyword=self.keyword).get()
            if item.model:
                regressor = pickle.loads(item.model)
            papers = item.papers
            x = [vectorize_paper(paper) for paper in papers]
            y = regressor.predict(x)
            # return papers
            return itemgetter(*[t[0] for t in sorted(enumerate(y), key=lambda i: i[1], reverse=True)])(papers)
        except Exception as e:
            logging.debug(e)
            return None

    # def add_missing_info(self):
    #     self.add_journal_if_self()

    # # TODO jounal if
    # def add_journal_if_self(self):
    #     for k,v in self.papers.items():
    #         if 'Journal' not in v or not v['Journal']:
    #             v["Journal_IF"] = 0
    #             continue
    #         try:
    #             stripped_journal_name = re.sub('[\W_]+', '', v["Journal"].upper())
    #             v["Journal_IF"] = Journal.get(name==stripped_journal_name).impact_factor
    #         except Exception as e:
    #             try:
    #                 if len(stripped_journal_name) >= 16:
    #                     v["Journal_IF"] = Journal.get(
    #                         name.startswith(stripped_journal_name[:16])).impact_factor
    #                 if len(stripped_journal_name) >= 12:
    #                     v["Journal_IF"] = Journal.get(name.startswith(stripped_journal_name[:12])).impact_factor
    #                 elif len(stripped_journal_name) >= 8:
    #                     v["Journal_IF"] = Journal.get(name.startswith(stripped_journal_name[:8])).impact_factor
    #                 elif len(stripped_journal_name) >= 4:
    #                     v["Journal_IF"] = Journal.get(name.startswith(stripped_journal_name[:4])).impact_factor
    #                 else:
    #                     v["Journal_IF"] = 0
    #             except Exception as e:
    #                 v["Journal_IF"] = 0

    # @staticmethod
    # def add_journal_if(paper_list):
    #     for paper in paper_list:
    #         if 'Journal' not in paper or not paper['Journal']:
    #             paper["Journal_IF"] = 0
    #             continue
    #         try:
    #             stripped_journal_name = re.sub('[\W_]+', '', paper["Journal"].upper())
    #             paper["Journal_IF"] = Journal.get(Journal.title==stripped_journal_name).impact_factor
    #         except DoesNotExist:
    #             try:
    #                 if len(stripped_journal_name) >= 16:
    #                     paper["Journal_IF"] = Journal.get(
    #                         Journal.title.startswith(stripped_journal_name[:16])).impact_factor
    #                 if len(stripped_journal_name) >= 12:
    #                     paper["Journal_IF"] = Journal.get(Journal.title.startswith(stripped_journal_name[:12])).impact_factor
    #                 elif len(stripped_journal_name) >= 8:
    #                     paper["Journal_IF"] = Journal.get(Journal.title.startswith(stripped_journal_name[:8])).impact_factor
    #                 elif len(stripped_journal_name) >= 4:
    #                     paper["Journal_IF"] = Journal.get(Journal.title.startswith(stripped_journal_name[:4])).impact_factor
    #                 else:
    #                     paper["Journal_IF"] = 0
    #             except DoesNotExist:
    #                 paper["Journal_IF"] = 0

    # def ranking(self):
    #     model = self.check_model()
    #     if model:
    #         clf = model[0]
    #         number_clicks = model[1]
    #         maximum_ml_score = -1
    #         for k,v in self.papers.items():
    #             if "Journal_IF" in v and "Year" in v:
    #                 x = [[v["Year"], v["Journal_IF"]]]
    #                 score_ml = clf.predict(x)[0]
    #                 v["Score_ML"] = score_ml
    #                 if score_ml > maximum_ml_score:
    #                     maximum_ml_score = score_ml
    #                 weight = 1 - math.pow(0.5, 0.1*number_clicks)
    #                 v["Weight"] = weight
    #         for k,v in self.papers.items():
    #             if "Score_ML" in v:
    #                 v["Score_ML"] *= 1 / maximum_ml_score
    #                 # logging.debug("{}: {}".format(v["Title"], v["Score_ML"]))
    #                 v["Score"] = v["Score"]*(1-v["Weight"]) + v["Score_ML"]*v["Weight"]
    #     else:
    #         pass

    # TODO: models
    # def check_model(self):
    #     ALWAYS_CREATE_NEW_MODEL_AND_DONT_SAVE = True
    #     if ALWAYS_CREATE_NEW_MODEL_AND_DONT_SAVE:
    #         new_model = self.train_model()
    #         return new_model
    #     try:
    #         search_term = SearchTerm.get(SearchTerm.keyword == self.keyword)
    #         model = Model.get(Model.search_term == search_term)
    #         if datetime.datetime.now() - model.last_modified > datetime.timedelta(days = 1):
    #             new_model = self.train_model()
    #             if new_model:
    #                 model.model = pickle.dumps(new_model)
    #                 model.last_modified = datetime.datetime.now()
    #                 model.save()
    #             return new_model
    #         else:
    #             return pickle.loads(model.model)
    #     except DoesNotExist:
    #         new_model = self.train_model()
    #         if new_model:
    #             Model.create(
    #                 search_term = SearchTerm.get(SearchTerm.keyword == self.keyword),
    #                 model = pickle.dumps(new_model)
    #             )
    #         return new_model

    # def train_model(self):
    #     x, y = [], []
    #     #clicks = SearchTerm.get(SearchTerm.keyword == self.keyword).clicks
    #     clicks = Click.select(Paper, Click).join(Paper).switch(Click).join(SearchTerm).where(SearchTerm.keyword == self.keyword)
    #     if clicks.count() == 0:
    #         return False
    #     for click in clicks:
    #         x.append(
    #             [
    #                 click.paper.year,
    #                 click.paper.journal_if
    #             ]
    #         )
    #         y.append(click.click_count)
    #     #clf = svm.SVR(kernel="rbf")
    #     #clf.fit(x, y)
    #     #return [clf, sum(y)]
    #     gp = gaussian_process.GaussianProcess(theta0=1e-2, thetaL=1e-4, thetaU=1e-1)
    #     gp.fit(x, y)
    #     return [gp, sum(y)]