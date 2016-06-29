import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import ../db.py
import db
from db import *
import logging
import re

journals = {}

def read_if():
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
        Journal.create(title = k, impact_factor = v[0], eigenfactor_score = v[1])


if __name__ == '__main__':
    read_if()