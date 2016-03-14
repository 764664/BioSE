from paper_processor import PaperProcessor
import logging
import itertools
import csv
from sklearn.cross_validation import KFold
import numpy as np
import random
from sklearn import gaussian_process
from sklearn import svm
from sklearn import linear_model

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s')


def build_author_network(papers):
    h = {}
    for paper in papers:
        if 'Author' in paper:
            authors = paper['Author'].split(", ")
            if len(authors) > 1:
                for pair in itertools.combinations(authors, 2):
                    pair = sorted(pair)
                    if pair[0] not in h:
                        h[pair[0]] = {}
                    if pair[1] not in h[pair[0]]:
                        h[pair[0]][pair[1]] = 0
                    h[pair[0]][pair[1]] += 1
                    if pair[1] not in h:
                        h[pair[1]] = {}
                    if pair[0] not in h[pair[1]]:
                        h[pair[1]][pair[0]] = 0
                    h[pair[1]][pair[0]] += 1
    return h

def build_author_score(papers):
    h = {}
    paper_num = len(papers)
    local_papers = papers.copy()
    local_papers.sort(key=lambda x:x['PubMedRanking'])
    for idx, paper in enumerate(local_papers):
        paper['LocalPubMedRanking'] = idx
    for paper in local_papers:
        if 'Author' in paper:
            authors = paper['Author'].split(", ")
            for author in authors:
                if author not in h:
                    h[author] = 0

                if paper_num - paper['LocalPubMedRanking'] <= 0:
                    print("{} - {}".format(paper_num, paper['LocalPubMedRanking']))

                h[author] += (paper_num - paper['LocalPubMedRanking'])/paper_num
    return h

def save_author_network(h):
    with open("author_network.csv", "w", newline='') as csvfile:
        for i, j in h.items():
            for m, n in j.items():
                csv.writer(csvfile).writerow([i,m,n])
                # print("{}|{}|{}".format(i,m,n), file=f)

def cv_author_network(papers):
    kf = KFold(len(papers), n_folds=5, shuffle=True)
    papers = np.array(papers)
    size = len(papers)
    total_average_difference = 0
    zeros = 0
    for train, test in kf:
        train_set = list(papers[train])
        test_set = list(papers[test])
        test_size = len(test)
        average_difference = 0
        random_average_difference = 0

        author_network = build_author_network(train_set)
        author_score = build_author_score(train_set)

        for paper in test_set:
            assert 'Author' in paper
            score = 0
            authors = paper['Author'].split(", ")
            for author in authors:
                if author in author_score:
                    score += author_score[author]
                if author in author_network:
                    for related_author, collaborations in author_network[author].items():
                        score += author_score[related_author] * collaborations / 100
            paper['TestScore'] = score
            if score == 0:
                zeros += 1/size
            # logging.debug("{}: {}".format(paper['Title'], score))

        test_set.sort(key=lambda x: x["PubMedRanking"])
        for idx, paper in enumerate(test_set):
            paper['ReferenceRanking'] = idx
        test_set.sort(key=lambda x: x["TestScore"])
        test_set.reverse()
        for idx, paper in enumerate(test_set):
            difference = abs(idx-paper['ReferenceRanking']) / test_size
            average_difference += difference / test_size
        # random.shuffle(test_set)
        # for idx, paper in enumerate(test_set):
        #     difference = abs(idx-paper['ReferenceRanking']) / test_size
        #     random_average_difference += difference / test_size
        # print("Average difference: {}".format(average_difference))
        # print("Random average difference: {}".format(random_average_difference))
        total_average_difference += average_difference / 5
    print("Total Average Difference: {}".format(total_average_difference))
    print("Zeros: {}".format(zeros))

def cv(papers):
    kf = KFold(len(papers), n_folds=5, shuffle=True)
    papers = np.array(papers)
    size = len(papers)
    total_average_difference = 0
    zeros = 0
    for train, test in kf:
        train_set = list(papers[train])
        test_set = list(papers[test])
        random.shuffle(test_set)
        test_size = len(test)
        average_difference = 0
        random_average_difference = 0

        x = []
        y = []
        for paper in train_set:
            x.append([paper['Journal_IF'], paper['Year']])
            y.append(size - paper["PubMedRanking"])
        # gp = gaussian_process.GaussianProcessRegressor(theta0=1e-2, thetaL=1e-4, thetaU=1e-1)
        # gp.fit(x, y)
        clf = svm.SVR(kernel="rbf")
        # clf = linear_model.LinearRegression()
        clf.fit(x, y)
        # print(clf.support_vectors_.shape)
        for paper in test_set:
            assert 'Author' in paper
            score = clf.predict([[paper['Journal_IF'], paper['Year']]])[0]
            # score = gp.predict([[paper['Journal_IF'], paper['Year']]])[0]
            # paper['TestScore'] = score
            paper['TestScore'] = random.random()
            # logging.debug("{}: {}".format(paper['Title'], score))

        test_set.sort(key=lambda x: x["PubMedRanking"])
        for idx, paper in enumerate(test_set):
            paper['ReferenceRanking'] = idx
        test_set.sort(key=lambda x: x["TestScore"])
        test_set.reverse()
        for idx, paper in enumerate(test_set):
            difference = abs(idx-paper['ReferenceRanking']) / test_size
            average_difference += difference / test_size
        total_average_difference += average_difference / 5
    print("Total Average Difference: {}".format(total_average_difference))

# q = "levamisole inhibitor"
# q = "levamisole"
# q = "phosphorylation"
# q = "methylation"
# q = "p53"
q = "homo sapiens"
p = PaperProcessor(q, num_of_documents=10000)
p.add_missing_info()
for i in range(3):
    cv(list(p.papers.values()))