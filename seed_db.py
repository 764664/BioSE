from db import *
import instant_search
import string
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Starting Execution.")
database.connect()
SearchTerm.create_table(True)
SearchLog.create_table(True)
Paper.create_table(True)
Click.create_table(True)
Model.create_table(True)
Journal.create_table(True)
InstantSearch.create_table(True)



def process_one_instant_search(s, instant):
    i, created = InstantSearch.get_or_create(keyword=s, defaults={"result": ",".join(instant.search(s))})
    i.save()

def process_instant_search():
    logging.info("Initiating instant search database")
    instant = instant_search.InstantSearch(load_db=False)
    for a in string.ascii_lowercase:
        process_one_instant_search(a, instant)
        for b in string.ascii_lowercase:
            process_one_instant_search(a+b, instant)
        logging.info("Finished {}/26".format(string.ascii_lowercase.index(a)+1))

process_instant_search()

database.close()
logging.info("Finishing Execution.")