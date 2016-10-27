from pubmed import PubMedFetcher
from models import *
from paper_processor import PaperProcessor
from sklearn.cross_validation import KFold
import numpy as np
import logging
import pickle
import hashlib
import os.path
import csv
import random
import scipy.stats
from IPython import embed

class NewEvaluation:
    def __init__(self, papers, query, model=Model, scaling_factors=[1], noise=False):
        self.noise = noise
        self.model = model
        self.model_name = model.__name__
        self.result = 0

        result = []
        final_score = []
        for i in scaling_factors:
            scores, len_papers = self.evaluate(papers, query, i)
            result.append(scores)
        for i in range(3):
            final_score.append(sum([one[i] for one in result])/len(result))
        self.result = final_score

        logging.info("Query: {}, Num:{}, Model: {}, Total Average: {}".format(query, len(papers), model, final_score))

    def calculate_md(self, x, y):
        n = len(x)
        _sum = 0
        for i in range(n):
            diff = abs(x[i] - y[i])
            _sum += diff
        ave = _sum / n / n
        return ave

    def evaluate(self, papers, query, scaling_factor):
        papers = np.array(papers)
        # logging.info("Got {} papers for query \"{}\", scaling_factor={}".format(len(papers), query, scaling_factor))

        all_time_result = 0

        times = 1
        for i in range(1, times+1):
            metrics = [0, 0, 0]
            kf = KFold(len(papers), 5, shuffle=True, random_state=42)
            for train, test in kf:
                train_set = papers[train]
                test_set = papers[test]
                # train_set = papers
                # test_set = papers
                for train_sample in train_set:
                    score = len(papers) - train_sample["ReferenceRank"] + 1
                    # Gaussian noise
                    # Standard Variation: Score/5
                    score = 1 if score == 0 else abs(score)
                    noise = np.random.normal(0, score / 200)

                    score *= scaling_factor
                    if self.noise:
                        score += noise

                    train_sample["Score"] = score

                for test_sample in test_set:
                    test_sample["Score"] = random.random()

                self.model(train_set, test_set, query)

                test_set = list(test_set)
                test_size = len(test_set)
                test_set.sort(key = lambda x: x["ReferenceRank"])
                for idx, test_sample in enumerate(test_set):
                    test_sample["Correct_Ranking"] = idx

                total_diff = 0
                test_set.sort(key = lambda x: x["Score"])
                test_set.reverse()
                x = list(range(1, len(test_set)+1))
                y = [one['Correct_Ranking'] for one in test_set]

            # logging.info("Test size: {}".format(test_size))
            #     for idx, test_sample in enumerate(test_set):
            #         total_diff += abs(test_sample["Correct_Ranking"] - idx) / test_size
            #     ave_diff = total_diff / test_size

                metrics[0] += self.calculate_md(x, y) / 5
                metrics[1] += scipy.stats.pearsonr(x, y)[0] / 5
                metrics[2] += scipy.stats.kendalltau(x, y)[0] / 5
            # all_time_result += overall_diff / times

            # logging.info("{}th trial, Average Difference: {}".format(i, overall_diff))

        # logging.info("For all trials, Average Difference: {}".format(all_time_result))
        return metrics, len(papers)

class Evaluation:
    def __init__(self, queries, model=Model, num_of_papers=10000, scaling_factors=[1], noise=False):
        self.num_of_papers = num_of_papers
        self.noise = noise
        self.model = model
        self.model_name = model.__name__

        len_papers = 0
        total_average = 0
        for query in queries:
            result = []
            for i in scaling_factors:
                score, len_papers = self.evaluate(query, i)
                result.append(score)
            result.append(sum(result)/len(result))
            total_average += sum(result)/len(result)/len(queries)

            with open('tmp/' + self.model_name + '.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([query, len_papers] + result)

        logging.info("Total Average: {}".format(total_average))

    def evaluate(self, query, scaling_factor):
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
        logging.info("Got {} papers for query \"{}\", scaling_factor={}".format(len(papers), query, scaling_factor))

        all_time_result = 0

        times = 1
        for i in range(1, times+1):
            overall_diff = 0
            kf = KFold(len(papers), 5, shuffle=True)
            for train, test in kf:
                train_set = papers[train]
                test_set = papers[test]

                for train_sample in train_set:
                    score = len(papers) - train_sample["Ranking"] + 1
                    # Gaussian noise
                    # Standard Variation: Score/5
                    score = 1 if score == 0 else abs(score)
                    noise = np.random.normal(0, score / 5)

                    score *= scaling_factor
                    if self.noise:
                        score += noise

                    train_sample["Score"] = score

                # for test_sample in test_set:
                #     test_sample["Score"] = np.random.rand()

                self.model(train_set, test_set, query)

                test_set = list(test_set)
                test_size = len(test_set)
                test_set.sort(key = lambda x: x["Ranking"])
                for idx, test_sample in enumerate(test_set):
                    test_sample["Correct_Ranking"] = idx

                total_diff = 0
                test_set.sort(key = lambda x: x["Score"])
                test_set.reverse()
                # logging.info("Test size: {}".format(test_size))
                for idx, test_sample in enumerate(test_set):
                    total_diff += abs(test_sample["Correct_Ranking"] - idx) / test_size
                ave_diff = total_diff / test_size
                overall_diff += ave_diff / 5

            all_time_result += overall_diff / times

            # logging.info("{}th trial, Average Difference: {}".format(i, overall_diff))

        # logging.info("For all trials, Average Difference: {}".format(all_time_result))
        return all_time_result, len(papers)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # queries = ["methylation"]
    scaling_factors = [1, 0.1, 0.01, 0.001]
    # scaling_factors = [1]
    queries = ["methylation", "RNA-Seq", "homo sapiens", "p53", "alignment"]
    Evaluation(queries, model=Model12, num_of_papers=10000, scaling_factors=scaling_factors, noise=True)