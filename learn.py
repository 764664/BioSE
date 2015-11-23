from db import *
from sklearn import svm
import logging
import time
import subprocess

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')

journalif = {}

database.connect()


def add_missing_info():
    read_if()
    for item in Visit.select():
        if item.completed:
            print("Continue")
            continue
        if item.journal:
            item.journalif = 2
            if item.journal.upper() in journalif:
                item.journalif = journalif[item.journal.upper()]
            else:
                for key in journalif.keys():
                    if item.journal.upper() in key:
                        item.journalif = journalif[key]
        if item.citations == -1:
            item.citations = get_citations(item)
        item.completed = True
        item.save()


def get_citations(item):
    time.sleep(3)
    with subprocess.Popen(
            (
            "python3", "scholar.py", "-c", "1", "-p",
            item.title, "--csv-header"),
            stdout=subprocess.PIPE
    ) as proc:
        s = proc.stdout.read()
        index_citations = None
        for idx, item in enumerate(map(str.rstrip,
                                   s.decode().split("\n"))):
            if idx == 0:
                for idx2, word in enumerate(item.split("|")):
                    if word == "num_citations":
                        index_citations = idx2
            else:
                if item:
                    splited = item.split("|")
                    if index_citations is not None:
                        return int(splited[index_citations])
    return 1


def read_if():
    try:
        f = open("2014_SCI_IF.csv", "r")
    except Exception as e:
        logging.warning(e)
        return
    for line in f:
        journalif[line.split(",")[1].upper()] = line.split(",")[3]


def learn():
    X = []
    y = []
    for item in Visit.select():
        X.append([item.year, item.citations, item.journalif])
        y.append(item.score)
    print(X)
    print(y)
    clf = svm.SVR(kernel="rbf")
    clf.fit(X, y)
    print(clf.predict([[2013, 1010, 10.81]]))
    print(clf.predict([[2015, 0, 0.933]]))
    print(clf.predict([[2000, 20, 10]]))
    print(clf.predict([[2015, 20, 10]]))
    print(clf.predict([[2000, 2000, 100]]))

add_missing_info()
learn()

database.close()
