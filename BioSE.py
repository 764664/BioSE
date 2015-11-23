from flask import Flask, current_app, redirect, g
from paper_processor import PaperProcessor
import json
import logging
import math
from db import *

RESULTS_PER_PAGE = 10

app = Flask(__name__)

results = {}
search_id_to_results = {}


@app.before_request
def before_request():
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def hello_world():
    return current_app.send_static_file('index.html')


@app.route('/basic_search/<keyword>/<int:page>')
def basic_search(keyword, page):
    search = Search(keyword=keyword)
    search.save()
    if keyword in results:
        query_result = results[keyword]
    else:
        query_result = PaperProcessor(keyword)
        results[keyword] = query_result
    if page <= 0 or (page-1)*RESULTS_PER_PAGE >= \
            len(query_result.papers_array):
        logging.warning("No result.")
        return ''
    search_id_to_results[search.id] = query_result
    return_value = json.dumps(
        [
            query_result.papers_array
            [(page-1)*RESULTS_PER_PAGE:page*RESULTS_PER_PAGE],
            math.ceil(len(query_result.papers_array)/RESULTS_PER_PAGE),  # 1
            query_result.failure_pubmed,  # 2 Boolean
            query_result.num_papers,  # 3 Integer
            search.id  # 4 Integer
        ]
    )
    return return_value


@app.route('/jump/<int:searchid>/<int:paperid>')
def jump(searchid, paperid):
    if searchid in search_id_to_results:
        query = search_id_to_results[searchid]
        page = round(paperid/RESULTS_PER_PAGE) + 1
        for i in range(
                (page-1)*RESULTS_PER_PAGE,
                min(len(query.papers_array), page*RESULTS_PER_PAGE)):
            print(i)
            visit = Visit(
                search=searchid,
                title=query.papers_array[i]["Title"],
            )
            if "Year" in query.papers_array[i]:
                visit.year = query.papers_array[i]["Year"]
            if "Citations" in query.papers_array[i]:
                visit.cications = query.papers_array[i]["Citations"]
            if "Journal" in query.papers_array[i]:
                visit.journal = query.papers_array[i]["Journal"]
            if "LastAuthor" in query.papers_array[i]:
                visit.last_author = query.papers_array[i]["LastAuthor"]
            if "Author" in query.papers_array[i]:
                visit.authors = query.papers_array[i]["Author"]
            if paperid == i:
                visit.score = 1
            else:
                visit.score = 0
            visit.save()
        return redirect(
            query.papers_array[paperid]["URL"]
        )
    else:
        abort(404)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')
    app.debug = True
    app.run(host='0.0.0.0')
