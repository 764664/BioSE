import random
import math
from sklearn import preprocessing

class RankingAI:
    @staticmethod
    def passthrough(papers):
        for idx, paper in enumerate(papers):
            paper["ReferenceRank"] = paper["Ranking"]

    @staticmethod
    def rank(papers, query):
        n = len(papers)
        for i in range(n):
            paper = papers[i]
            impact_factor = paper["Journal_IF"]
            year = paper["Year"] - 2000
            score = impact_factor + year
            paper["Tmp_Score"] = score
        papers.sort(key=lambda paper: paper["Tmp_Score"])
        papers.reverse()
        for idx, paper in enumerate(papers):
            paper["ReferenceRank"] = idx+1

    @staticmethod
    def rank_2(papers, query):
        n = len(papers)
        data = [[paper["Journal_IF"], paper["Year"]] for paper in papers]
        # normalized_data = preprocessing.normalize(data, axis=0)
        normalized_data = preprocessing.StandardScaler().fit_transform(data)
        for i in range(n):
            paper = papers[i]
            impact_factor = normalized_data[i][0]
            year = normalized_data[i][1]
            score = impact_factor + year
            paper["Tmp_Score"] = score
        papers.sort(key=lambda paper: paper["Tmp_Score"])
        papers.reverse()
        for idx, paper in enumerate(papers):
            paper["ReferenceRank"] = idx+1

    @staticmethod
    def rank_3(papers, query):
        # linear
        n = len(papers)
        data = [[paper["Journal_IF"], paper["Year"], paper["Abstract"].count(query), paper["Title"].count(query)] for paper in papers]
        # normalized_data = data
        normalized_data = preprocessing.StandardScaler().fit_transform(data)
        # print(normalized_data)
        for i in range(n):
            paper = papers[i]
            impact_factor = normalized_data[i][0]
            year = normalized_data[i][1]
            tf_abstract = normalized_data[i][2]
            tf_title = normalized_data[i][3]
            score = impact_factor + year + tf_abstract + tf_title
            paper["Tmp_Score"] = score
        papers.sort(key=lambda paper: paper["Tmp_Score"])
        papers.reverse()
        for idx, paper in enumerate(papers):
            paper["ReferenceRank"] = idx+1

    @staticmethod
    def rank_4(papers, query):
        # non-linear
        n = len(papers)
        data = [[paper["Journal_IF"], paper["Year"], paper["Abstract"].count(query), paper["Title"].count(query)] for paper in papers]
        # normalized_data = data
        normalized_data = preprocessing.StandardScaler().fit_transform(data)
        # print(normalized_data)
        for i in range(n):
            paper = papers[i]
            impact_factor = normalized_data[i][0]
            year = normalized_data[i][1]
            tf_abstract = normalized_data[i][2]
            tf_title = normalized_data[i][3]
            score = impact_factor + year + tf_abstract * tf_title
            paper["Tmp_Score"] = score
        papers.sort(key=lambda paper: paper["Tmp_Score"])
        papers.reverse()
        for idx, paper in enumerate(papers):
            paper["ReferenceRank"] = idx+1
