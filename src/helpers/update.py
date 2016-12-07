from src.models.subscription import Subscription
import time
import threading
import logging

def update_subscription():
    logging.info("Updating subscriptions.")
    Subscription.update_all()
    logging.info("Finished updating subscriptions. Sleep for 5 minutes")
    time.sleep(300)

def update():
    logging.info("Starting threads for updating.")
    t = threading.Thread(target=update_subscription)
    t.start()