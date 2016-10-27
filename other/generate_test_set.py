import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pubmed
from papers_csv_handler import CSVHandler
from paper_processor import PaperProcessor
import logging
from IPython import embed

logging.getLogger().setLevel(logging.DEBUG)
papers = list(pubmed.PubMedFetcher("homo sapiens", num_of_documents=2116).papers.values())
PaperProcessor.add_journal_if(papers)
CSVHandler.write_list_to_csv("test.csv", papers)
