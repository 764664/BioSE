import random

class RankingAI:
    @staticmethod
    def rank(papers):
        n = len(papers)
        for i in range(n):
            paper = papers[i]
            impact_factor = paper["Journal_IF"]
            year = paper["Year"]
            score = impact_factor + year
            paper["Tmp_Score"] = score
        papers.sort(key=lambda paper: paper["Tmp_Score"])
        papers.reverse()
        for idx, paper in enumerate(papers):
            paper["ReferenceRank"] = idx+1
