from src.models.subscription import Subscription
from src.models.schema import ClickCount, SearchItem, Journal
from src.helpers.vectorize_paper import vectorize_paper
from sklearn import linear_model, preprocessing, svm, tree, ensemble
import time
import threading
import logging
import pickle
import re

def update_subscription():
    logging.info("Updating subscriptions.")
    Subscription.update_all()

def update_model():
    logging.info("Updating models.")
    for item in SearchItem.objects:
        model = train_model(item)
        binary = pickle.dumps(model)
        item.update(set__model=binary)

def update_all():
    logging.info("Start updates.")
    update_subscription()
    update_model()
    logging.info("Finished updates. Sleep for 5 minutes")
    time.sleep(900)

def update():
    logging.info("Starting threads for updating.")
    t = threading.Thread(target=update_all)
    t.start()

def train_model(item):
    x, y = [], []
    if len(item.papers) > 0 and ClickCount.objects(search_item=item).count() > 0:
        try:
            click_counts = ClickCount.objects(search_item=item)
            h = {}
            for click_count in click_counts:
                h[str(click_count.paper.id)] = click_count.count
            for paper in item.papers:
                if str(paper.id) in h:
                    count = h[str(paper.id)]
                    print("yes")
                else:
                    count = 0
                x.append(vectorize_paper(paper))
                y.append(count)
            regressor = tree.DecisionTreeRegressor()
            regressor.fit(x, y)
            return regressor
        except:
            print(x)
            print(y)
    else:
        return None