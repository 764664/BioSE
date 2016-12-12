import time

from flask_login import login_required, current_user
from flask import g, abort, jsonify, redirect, request

from src.helpers.pubmed import PubMedFetcher
from src.models.schema import SubscriptionItem, User, Paper, Author
from src.helpers.store_paper import store_paper
from src.helpers.recommend_keyword import recommend_from_user
import logging
import random
from IPython import embed


class Subscription:
    @staticmethod
    def add(args):
        try:
            keyword = args.get('keyword')
            user = User.objects(id=current_user.id).get()
            if SubscriptionItem.objects(keyword=keyword).count() == 0:
                item = SubscriptionItem(keyword=keyword)
                item.save()
                Subscription.update(item)
            else:
                item = SubscriptionItem.objects(keyword=keyword).first()
            user.update(push__subscriptions=item)
            return jsonify(status='ok', item=item.serialize())
        except Exception as e:
            logging.warning(e)
            return jsonify(status='error')

    @staticmethod
    def delete(id):
        try:
            user = User.objects(id=current_user.id).get()
            item = SubscriptionItem.objects(id=id).get()
            user.update(pull__subscriptions=item)
            return jsonify(status='ok')
        except Exception as e:
            logging.warning(e)
            return jsonify(status='error')

    @staticmethod
    def update_all():
        for item in SubscriptionItem.objects():
            Subscription.update(item)
            time.sleep(5)

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
        user = User.objects(id=current_user.id).get()
        papers = Paper.objects(subscriptions__in=user.subscriptions).order_by('-date')
        return papers

    @staticmethod
    def index():
        user = User.objects(id=current_user.id).get()
        return user.subscriptions

    @staticmethod
    def show(id):
        try:
            count = request.args.get('count', 20)
            offset = int(request.args.get('offset', 0))
            item = SubscriptionItem.objects(id=id).get()
            papers = Paper.objects(subscriptions=item).order_by('-date').skip(offset).limit(count)
            if papers.count() > 0:
                return jsonify(response=[paper.serialize() for paper in papers])
            else:
                return jsonify(response=[], more=False)
        except Exception as e:
            logging.warning(e)
            logging.warning(id)
            return jsonify(error="error")

    @staticmethod
    def recommend():
        recommended = recommend_from_user(current_user)
        if len(recommended) > 15:
            return jsonify(response=random.sample(recommended, 15))
        else:
            return jsonify(response=recommended)

# item = SubscriptionItem.objects.first()
# Subscription.update(item)
# print(Subscription.get_timeline())