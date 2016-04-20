class AbstractProcessor:
    def __init__(self):
        pass

    # def process_dict(self):
    #     for paper in self.papers.values():
    #         abstract = paper["Abstract"]
    #         words = list(set([x.strip().strip(",.").lower() for x in abstract.split()]))
    #         for word in words:
    #             if word not in self.bag:
    #                 self.bag[word] = 1
    #             else:
    #                 self.bag[word] += 1

    def process_list(self, papers):
        bag = {}
        for paper in papers:
            abstract = paper["Abstract"]
            words = list(set([x.strip().strip(",.").lower() for x in abstract.split()]))
            for word in words:
                if word not in bag:
                    bag[word] = 1
                else:
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