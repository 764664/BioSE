from collections import defaultdict
from vocabulary import Vocabulary

class AbstractProcessor:
    def __init__(self):
        self.common_words = ["all", "other"]

    # def process_dict(self):
    #     for paper in self.papers.values():
    #         abstract = paper["Abstract"]
    #         words = list(set([x.strip().strip(",.").lower() for x in abstract.split()]))
    #         for word in words:
    #             if word not in self.bag:
    #                 self.bag[word] = 1
    #             else:
    #                 self.bag[word] += 1

    # def process_list(self, papers):
    #     bag = defaultdict(int)
    #     for paper in papers:
    #         abstract = paper["Abstract"]
    #         words = list(set([x.strip().strip(",.").lower() for x in abstract.split()]))
    #         for word in words:
    #             bag[word] += 1
    #     return bag

    def process_list(self, papers):
        bag = defaultdict(int)
        voc = Vocabulary()
        for paper in papers:
            abstract = paper["Abstract"]
            words = list(set([x.strip().strip(",.").lower() for x in abstract.split()]))
            for word in words:
                if word not in self.common_words and voc.exact_search(word):
                    bag[word] += 1
        return bag

if __name__ == "__main__":
    papers = {
        "123": {
            "Abstract": "try this"
        },
        "234": {
            "Abstract": "try that"
        }
    }
    a = AbstractProcessor(papers)
    print(a.bag)