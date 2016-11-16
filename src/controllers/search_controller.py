import datetime
import json
import logging
import math

import flask_login
from flask import g

from src.helpers.abstract_processor import AbstractProcessor
from src.helpers.paper_processor import PaperProcessor
from src.models.schema import User, SearchItem, SearchHistory

RESULTS_PER_PAGE = 10

class SearchController:
    @staticmethod
    def search(keyword, args):
        # Get request arguments
        page = int(args.get('page', ''))
        order_by = args.get('order_by', '')
        filter_by = args.get('filter_by', '')

        # Store history in database
        if SearchItem.objects(keyword=keyword).count() == 0:
            search_item = SearchItem(keyword=keyword)
        else:
            search_item = SearchItem.objects(keyword=keyword).get()
        search_item.count += 1
        search_item.save()

        if flask_login.current_user.is_authenticated:
            search_history = SearchHistory(item=search_item, user=User.objects(id=flask_login.current_user.id).get())
        else:
            search_history = SearchHistory(item=search_item)
        search_history.save()

        # Load cache
        search_results = g.get('search_results', None)
        if search_results is None:
            g.search_results = {}
            search_results = g.search_results

        search_id_to_results = g.get('search_id_to_results', None)
        if search_id_to_results is None:
            g.search_id_to_results = {}
            search_id_to_results = g.search_id_to_results

        if keyword in search_results:
            query_result = search_results[keyword]
        else:
            query_result = PaperProcessor(keyword)
            search_results[keyword] = query_result
        if page <= 0 or (page - 1) * RESULTS_PER_PAGE >= \
                len(query_result.papers_array):
            logging.warning("No result.")
            return ''
        search_id_to_results[str(search_item.id)] = query_result


        # Filtering
        logging.debug("Order by : " + order_by)
        if order_by == "Default":
            # logging.debug("Order by default")
            query_result.papers_array.sort(key=lambda x: x["Score"], reverse=True)
        else:
            for paper in query_result.papers_array:
                try:
                    paper["ParsedDate"] = datetime.datetime.strptime(paper["PubDate"], "%Y %b %d").strftime("%Y%m%d")
                except:
                    try:
                        paper["ParsedDate"] = datetime.datetime.strptime(paper["PubDate"], "%Y %b").strftime("%Y%m%d")
                    except:
                        try:
                            paper["ParsedDate"] = datetime.datetime.strptime(paper["PubDate"], "%Y").strftime("%Y%m%d")
                        except:
                            paper["ParsedDate"] = "19000000"

        if order_by == "Publication Date(Ascending)":
            query_result.papers_array.sort(key=lambda x: x["ParsedDate"])

        if order_by == "Publication Date(Descending)":
            query_result.papers_array.sort(key=lambda x: x["ParsedDate"], reverse=True)

        logging.debug("Filter by : " + filter_by)

        if filter_by!="Default":
            return_list = [paper for paper in query_result.papers_array if paper["Abstract"].lower().find(filter_by) != -1]
        else:
            return_list = query_result.papers_array

        # Word bag
        bag = AbstractProcessor().process_list(return_list)
        words = [[y, bag[y]] for y in sorted(list(bag.keys()), key=lambda x: bag[x], reverse=True)[:30]]

        # Return result
        return_value = json.dumps(
            {
                "success": True,
                "errors": [],
                "result": return_list[(page-1)*RESULTS_PER_PAGE:page*RESULTS_PER_PAGE],
                "result_info": {
                    "page": math.ceil(len(return_list)/RESULTS_PER_PAGE),
                    "count": len(return_list),
                    "id": str(search_item.id),
                    "failure_pubmed": query_result.failure_pubmed,
                    "words": words
                }
            }
        )
        return return_value