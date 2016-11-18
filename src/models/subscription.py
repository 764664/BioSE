import time

import flask_login

from src.helpers.pubmed import PubMedFetcher
from src.models.schema import SubscriptionItem, User, Paper, Author
from src.helpers.store_paper import store_paper


class Subscription:
    @staticmethod
    def add(keyword):
        user = User.objects(id=flask_login.current_user.id).get()
        if SubscriptionItem.objects(keyword=keyword).count() == 0:
            item = SubscriptionItem(keyword=keyword)
            item.save()
            # t = threading.Thread(target=Subscription.update, args=(item,))
            # t.start()
            Subscription.update(item)
        else:
            item = SubscriptionItem.objects(keyword=keyword).first()
        user.update(push__subscriptions=item)


    @staticmethod
    def update_all():
        for item in SubscriptionItem.objects():
            Subscription.update(item)
            time.sleep(2)

    @staticmethod
    def update(item):
        keyword = item.keyword
        papers_existing_in_item = [x.id for x in item.papers]
        p = PubMedFetcher(keyword, num_of_documents=10, sort="pub+date")
        for paper in p.papers.values():
            paper_mongo = store_paper(paper)
            if paper_mongo.id not in papers_existing_in_item:
                item.update(push__papers=paper_mongo)
                paper_mongo.update(push__subscriptions=item)

    @staticmethod
    def get_timeline():
        user = User.objects(id=flask_login.current_user.id).get()
        papers = Paper.objects(subscriptions__in=user.subscriptions).order_by('-date')
        return papers

    @staticmethod
    def index():
        user = User.objects(id=flask_login.current_user.id).get()
        return user.subscriptions
# item = SubscriptionItem.objects.first()
# Subscription.update(item)
# print(Subscription.get_timeline())