from pubmed import PubMedFetcher
from models.basic import BasicEvaluator
from paper_processor import PaperProcessor
from sklearn.cross_validation import KFold
import numpy as np
import logging
import pickle
import hashlib
import os.path

class Evaluation:
    def __init__(self, queries, num_of_papers=1000, scaling_factor=1, noise=False):
        # queries = ["methylation", "RNA-Seq", "homo sapiens", "p53"]
        queries = ["methylation"]
        self.num_of_papers = num_of_papers
        self.scaling_factor = scaling_factor
        self.noise = noise
        for query in queries:
            self.evaluate(query)

    def evaluate(self, query):
        m = hashlib.md5(str.encode(query+str(self.num_of_papers)))
        digest = m.hexdigest()
        filename = "tmp/"+digest
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                pubmed = pickle.load(f)
        else:
            pubmed = PaperProcessor(query, num_of_documents=self.num_of_papers, postprocessing=False)
            pubmed.add_missing_info()
            with open(filename, 'wb') as f:
                pickle.dump(pubmed, f)

        # pubmed.add_missing_info()

        # c = 0
        # for value in pubmed.papers.values():
        #     if value['Journal_IF'] == 0:
        #         c += 1
        #
        # print(c)


        papers = np.array(list(pubmed.papers.values()))
        logging.info("Got {} papers for query {}".format(len(papers), query))

        all_time_result = 0

        times = 5
        for i in range(1, times+1):
            overall_diff = 0
            kf = KFold(len(papers), 5, shuffle=True)
            for train, test in kf:
                train_set = papers[train]
                test_set = papers[test]
                test_size = len(test)

                for train_sample in train_set:
                    score = len(papers) - train_sample["Ranking"] + 1
                    # Gaussian noise
                    # Standard Variation: Score/5
                    score = 1 if score==0 else abs(score)
                    noise = np.random.normal(0, score / 5)

                    score *= self.scaling_factor
                    if self.noise:
                        score += noise

                    train_sample["Score"] = score

                for test_sample in test_set:
                    test_sample["Score"] = np.random.rand()

                BasicEvaluator.evaluate(train_set, test_set)

                test_set = list(test_set)
                test_set.sort(key = lambda x: x["Ranking"])
                for idx, test_sample in enumerate(test_set):
                    test_sample["Test_Ranking"] = idx

                total_diff = 0
                test_set.sort(key = lambda x: x["Score"])
                test_set.reverse()
                # logging.info("Test size: {}".format(test_size))
                for idx, test_sample in enumerate(test_set):
                    total_diff += abs(test_sample["Test_Ranking"] - idx) / test_size
                ave_diff = total_diff / test_size
                overall_diff += ave_diff / 5

            all_time_result += overall_diff / times

            logging.info("{}th trial, Average Difference: {}".format(i, overall_diff))

        logging.info("For all trials, Average Difference: {}".format(all_time_result))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    Evaluation()