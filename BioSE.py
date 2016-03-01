from flask import Flask, current_app, redirect, g, abort, request
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
    search = SearchLog.create(keyword=keyword)
    SearchTerm.get_or_create(keyword = keyword)
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
    # return_value = json.dumps(
    #     [
    #         query_result.papers_array
    #         [(page-1)*RESULTS_PER_PAGE:page*RESULTS_PER_PAGE],
    #         math.ceil(len(query_result.papers_array)/RESULTS_PER_PAGE),  # 1
    #         query_result.failure_pubmed,  # 2 Boolean
    #         query_result.num_papers,  # 3 Integer
    #         search.id  # 4 Integer
    #     ]
    # )
    return_value = json.dumps(
        {
            "success": True,
            "errors": [],
            "result": query_result.papers_array[(page-1)*RESULTS_PER_PAGE:page*RESULTS_PER_PAGE],
            "result_info": {
                "page": math.ceil(len(query_result.papers_array)/RESULTS_PER_PAGE),
                "count": query_result.num_papers,
                "id": search.id,
                "failure_pubmed": query_result.failure_pubmed
            }
        }
    )
    return return_value

@app.route('/search/<keyword>')
def search(keyword):
    logging.debug(request.form)

    page = int(request.args.get('page', ''))


    search = SearchLog.create(keyword=keyword)
    SearchTerm.get_or_create(keyword = keyword)
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

    logging.debug(request.args.get('order_by', ''))
    if request.args.get('order_by', '') == "Default":
        logging.debug("Order by default")
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

    if request.args.get('order_by', '') == "Publication Date(Ascending)":
        query_result.papers_array.sort(key=lambda x: x["ParsedDate"])

    if request.args.get('order_by', '') == "Publication Date(Descending)":
        query_result.papers_array.sort(key=lambda x: x["ParsedDate"], reverse=True)

    return_value = json.dumps(
        {
            "success": True,
            "errors": [],
            "result": query_result.papers_array[(page-1)*RESULTS_PER_PAGE:page*RESULTS_PER_PAGE],
            "result_info": {
                "page": math.ceil(len(query_result.papers_array)/RESULTS_PER_PAGE),
                "count": query_result.num_papers,
                "id": search.id,
                "failure_pubmed": query_result.failure_pubmed
            }
        }
    )
    return return_value

@app.route('/jump/<int:search_id>/<int:paper_id>')
def jump(search_id, paper_id):
    if search_id in search_id_to_results:
        query = search_id_to_results[search_id]
        try:
            search_term_text = SearchLog.get(SearchLog.id == search_id).keyword
            local_search_term = SearchTerm.get(SearchTerm.keyword == search_term_text)
        except DoesNotExist:
            logging.error("Search log doesn't exist.")
        page = math.floor(paper_id/RESULTS_PER_PAGE) + 1
        for i in range(
                (page-1)*RESULTS_PER_PAGE,
                min(len(query.papers_array), page*RESULTS_PER_PAGE)):
            logging.info("Processing paperid {} i {} title {}".format(paper_id, i, query.papers_array[i]["Title"]))
            local_paper, created = Paper.get_or_create(title = query.papers_array[i]["Title"])
            if created:
                logging.info("Created No.{} title {}".format(i, query.papers_array[i]["Title"]))
            if created:
                if "Year" in query.papers_array[i]:
                    local_paper.year = query.papers_array[i]["Year"]
                if "Citations" in query.papers_array[i]:
                    local_paper.citations = query.papers_array[i]["Citations"]
                if "Journal" in query.papers_array[i]:
                    local_paper.journal = query.papers_array[i]["Journal"]
                if "LastAuthor" in query.papers_array[i]:
                    local_paper.last_author = query.papers_array[i]["LastAuthor"]
                if "Author" in query.papers_array[i]:
                    local_paper.authors = query.papers_array[i]["Author"]
                if "Journal_IF" in query.papers_array[i]:
                    local_paper.journal_if = query.papers_array[i]["Journal_IF"]
                if paper_id == i:
                    local_paper.score = 1
                else:
                    local_paper.score = 0
                local_paper.save()
            print(local_search_term)
            click, created = Click.get_or_create(search_term = local_search_term, paper = local_paper)
            if paper_id == i:
                click.click_count += 1
                click.save()
        return redirect(
            query.papers_array[paper_id]["URL"]
        )
    else:
        abort(404)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')
    app.debug = True
    app.run(host='0.0.0.0')
