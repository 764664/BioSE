import datetime
import json
import logging
import math

import flask_login
from flask import g, abort, jsonify, redirect

from src.helpers.abstract_processor import AbstractProcessor
from src.helpers.paper_processor import PaperProcessor
from src.models.schema import User, SearchItem, SearchHistory, Paper, ClickHistory, ClickCount
from src.helpers.store_paper import papers_searilizer
import pickle

RESULTS_PER_PAGE = 10

class SearchController:
    @staticmethod
    def search(args):
        keyword = args.get('keyword')

        # Store history in database
        if SearchItem.objects(keyword=keyword).count() == 0:
            search_item = SearchItem(keyword=keyword)
        else:
            search_item = SearchItem.objects(keyword=keyword).get()
        search_item.count += 1
        search_item.save()

        # Load cache
        # search_results = g.get('search_results', None)
        # if search_results is None:
        #     g.search_results = {}
        #     search_results = g.search_results
        #
        # search_id_to_results = g.get('search_id_to_results', None)
        # if search_id_to_results is None:
        #     g.search_id_to_results = {}
        #     search_id_to_results = g.search_id_to_results

        query_result = PaperProcessor(keyword)
        papers = query_result.papers_array

        # paper_ids = [x["DBID"] for x in papers]
        # search_item.update(add_to_set__papers=paper_ids)

        if flask_login.current_user.is_authenticated:
            search_history = SearchHistory(item=search_item,
                                           user=User.objects(id=flask_login.current_user.id).get(),
                                           papers=[x for x in query_result.papers_array])
        else:
            search_history = SearchHistory(item=search_item,
                                           papers=[x for x in query_result.papers_array])
        search_history.save()

        # # Word bag
        # bag = AbstractProcessor().process_list(return_list)
        # words = [[y, bag[y]] for y in sorted(list(bag.keys()), key=lambda x: bag[x], reverse=True)[:30]]

        # Return result
        return jsonify(
            response=str(search_history.id),
            meta_info={
                'page_count': math.ceil(len(papers)/RESULTS_PER_PAGE)
            }
        )
        # return_value = jsonify(
        #     {
        #         "success": True,
        #         "errors": [],
        #         "result": return_list[(page-1)*RESULTS_PER_PAGE:page*RESULTS_PER_PAGE],
        #         "result_info": {
        #             "page": math.ceil(len(return_list)/RESULTS_PER_PAGE),
        #             "count": len(return_list),
        #             "id": str(search_item.id),
        #             "failure_pubmed": query_result.failure_pubmed,
        #             "words": words
        #         },
        #         "search_history_id": str(search_history.id)
        #     }
        # )
        # return return_value

    @staticmethod
    def fetch(args):
        # Get request arguments
        page = int(args.get('page', 1))
        order_by = args.get('order_by', '')
        filter_by = args.get('filter_by', '')

        search_history_id = args.get("search_history_id")
        search_history = SearchHistory.objects(id=search_history_id).get()
        papers = search_history.papers

        if page <= 0 or (page - 1) * RESULTS_PER_PAGE >= len(papers):
            logging.warning("No more papers.")
            return jsonify(
                response=None,
                error="No more papers"
            )

        # Filtering
        # TODO : Outdated
        # logging.debug("Order by : " + order_by)
        # if order_by == "Default":
        #     # logging.debug("Order by default")
        #     query_result.papers_array.sort(key=lambda x: x["Score"], reverse=True)
        # else:
        #     for paper in query_result.papers_array:
        #         try:
        #             paper["ParsedDate"] = datetime.datetime.strptime(paper["PubDate"], "%Y %b %d").strftime("%Y%m%d")
        #         except:
        #             try:
        #                 paper["ParsedDate"] = datetime.datetime.strptime(paper["PubDate"], "%Y %b").strftime("%Y%m%d")
        #             except:
        #                 try:
        #                     paper["ParsedDate"] = datetime.datetime.strptime(paper["PubDate"], "%Y").strftime("%Y%m%d")
        #                 except:
        #                     paper["ParsedDate"] = "19000000"
        #
        # if order_by == "Publication Date(Ascending)":
        #     query_result.papers_array.sort(key=lambda x: x["ParsedDate"])
        #
        # if order_by == "Publication Date(Descending)":
        #     query_result.papers_array.sort(key=lambda x: x["ParsedDate"], reverse=True)
        #
        # logging.debug("Filter by : " + filter_by)
        #
        # if filter_by != "Default":
        #     return_list = [paper for paper in query_result.papers_array if
        #                    paper["Abstract"].lower().find(filter_by) != -1]
        # else:
        #     return_list = query_result.papers_array

        return jsonify(
            response=papers_searilizer(search_history.papers)
        )

    @staticmethod
    def jump(args):
        try:
            search_history_id = args.get('search_history_id')
            paper_id = args.get('paper_id')
            search_history = SearchHistory.objects(id=search_history_id).get()
            search_item = search_history.item
            paper = Paper.objects(id=paper_id).get()
            click_history = ClickHistory(
                search_item=search_item,
                search_history=search_history,
                paper=paper,
                user=User.objects(id=flask_login.current_user.id).get() if flask_login.current_user.is_authenticated else None
            )
            click_history.save()
            if ClickCount.objects(search_item=search_item, paper=paper).count() > 0:
                click_count = ClickCount.objects(search_item=search_item, paper=paper).get()

            else:
                click_count = ClickCount(
                    search_item=search_item, paper=paper
                )
            click_count.count = click_count.count + 1
            click_count.save()
            return redirect(paper.url)
        except Exception as e:
            logging.warning(e)
            abort(401)

