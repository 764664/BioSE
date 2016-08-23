from pubmed import PubMedFetcher
import csv
from ranking_ai import RankingAI
from paper_processor import PaperProcessor
from evaluation_dep import NewEvaluation
import logging
import hashlib, os, pickle
from models import *
import re

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

def run_one_query(query, num):
    papers = get_papers_from_pubmed(query, num)
    # papers = list(PubMedFetcher(query, num_of_documents=10).papers.values())
    PaperProcessor.add_journal_if(papers)
    RankingAI.rank(papers)
    # CSVHandler.write_list_to_csv("test.csv", papers, additional_fields=["ReferenceRank"])
    # scaling_factors = [1, 0.1, 0.01, 0.001]
    scaling_factors = [1]
    models = [Model1, Model2, Model3, Model4, Model5, Model6, Model7, Model8, Model9, Model10, Model11, Model12]
    results = [[] for _ in range(len(models))]
    for idx, model in enumerate(models):
        eva = NewEvaluation(papers, query, model=model, scaling_factors=scaling_factors, noise=False)
        results[idx].append(eva.result)
    
    with open('tmp/{}{}.csv'.format(query, len(papers)), 'w', newline='') as csvfile:
        fieldnames = ['Model No.', 'Description', 'Result']
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        for idx, result in enumerate(results):
            row = [re.search(r'(\d+)$', models[idx].__name__).group(0), models[idx].__doc__] + result
            writer.writerow(row)
        
query = "methylation"
num = 10000
run_one_query(query, num)