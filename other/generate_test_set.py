import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pubmed
from papers_csv_handler import CSVHandler
from paper_processor import PaperProcessor

papers = pubmed.PubMedFetcher("methylation", num_of_documents=5).papers
PaperProcessor.add_journal_if(papers)
CSVHandler.write_to_csv("test.csv", papers)
