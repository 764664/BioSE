from paper_processor import PaperProcessor
import logging

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')
q = "levamisole inhibitor"
p = PaperProcessor(q)
