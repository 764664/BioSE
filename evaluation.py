from pubmed import PubMedFetcher
import csv
from ranking_ai import RankingAI
from paper_processor import PaperProcessor
from evaluation_dep import NewEvaluation
import logging
import hashlib, os, pickle
from models import *
import re
import time
from IPython import embed

def get_papers_from_pubmed(query, num_of_papers):
    m = hashlib.md5(str.encode(query + str(num_of_papers)+"2"))
    digest = m.hexdigest()
    filename = "tmp/" + digest
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            papers = pickle.load(f)
    else:
        papers = list(PubMedFetcher(query, num_of_documents=num_of_papers).papers.values())
        with open(filename, 'wb') as f:
            pickle.dump(papers, f)
    return papers

logging.basicConfig(level=logging.DEBUG)

def run_one_query(query, num, models, ai=True, noise=False, rank=RankingAI.rank):
    papers = get_papers_from_pubmed(query, num)
    # papers = list(PubMedFetcher(query, num_of_documents=10).papers.values())
    PaperProcessor.add_journal_if(papers)
    if ai:
        rank(papers, query)
    else:
        RankingAI.passthrough(papers)
    # CSVHandler.write_list_to_csv("test.csv", papers, additional_fields=["ReferenceRank"])
    if noise:
        scaling_factors = [1, 0.1, 0.01, 0.001]
    else:
        scaling_factors = [1]

    results = [[] for _ in range(len(models))]
    times = [0 for _ in range(len(models))]
    for idx, model in enumerate(models):
        t = time.time()
        eva = NewEvaluation(papers, query, model=model, scaling_factors=scaling_factors, noise=noise)
        time_passed = time.time() - t
        times[idx] = time_passed
        results[idx].extend(eva.result)
    
    with open('tmp/{}{}.csv'.format(query, len(papers)), 'w', newline='') as csvfile:
        fieldnames = ['Model No.', 'Description', 'Result']
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        for idx, result in enumerate(results):
            row = [re.search(r'(\d+)$', models[idx].__name__).group(0), models[idx].__doc__] + result
            writer.writerow(row)

query = "methylation"
# query = "transcription factor"
# query = "single cell sequencing"
num = 10000
# model_no = [1, 2, 4, 6, 7, 8, 9, 11, 12, 14, 15, 16, 17]
# model_no = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17]
model_no = [2, 3, 7, 14, 15, 16]
models = [eval("Model{}".format(x)) for x in model_no]
# run_one_query(query, num, models, ai=True, noise=False, rank=RankingAI.rank_3)
# run_one_query(query, num, models, ai=True, noise=False, rank=RankingAI.rank_4)
# run_one_query(query, num, models, ai=True, noise=True, rank=RankingAI.rank_4)
run_one_query(query, num, models, ai=True, noise=False)
