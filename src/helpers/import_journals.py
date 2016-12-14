# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
import re
from src.models.schema import Journal

journals = {}

def read_if():
    print("Start to import journals")
    count = 0
    try:
        f = open("./resources/2014_SCI_IF.csv", "r")
    except Exception as e:
        logging.warning(e)
        return
    f.readline()
    for line in f:
        try:
            stripped_journal_name = re.sub('[\W_]+', '', line.split(",")[1].upper())
            journals[stripped_journal_name] = [float(line.split(",")[3]), float(line.split(",")[4])]
        except Exception:
            pass

    for k, v in journals.items():
        journal = Journal(name = k, impact_factor = v[0], eigenfactor_score = v[1])
        journal.save()
        count += 1
        if count % 100 == 0:
            print('.', end='', flush=True)
    print("\nFinished importing journals")

if __name__ == '__main__':
    read_if()