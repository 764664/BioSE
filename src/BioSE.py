from flask import Flask, current_app, redirect, g, abort, request, _app_ctx_stack, session, url_for, flash
import json
import logging
import math
import datetime
from flask_bcrypt import Bcrypt
from src import app
from src.paper_processor import PaperProcessor
from src.autocomplete import InstantSearch
from src.db import SearchLog, SearchTerm, Click, Paper, database
from src.db_mongo import User
from src.abstract import AbstractProcessor
from src.subscription import Subscription
import flask_login

RESULTS_PER_PAGE = 10

bcrypt = Bcrypt(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@app.before_request
def before_request():
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def index():
    return current_app.send_static_file('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        logging.debug("{} tries to login.".format(email))
        try:
            user = User.objects(email=email).get()
            if bcrypt.check_password_hash(user.password, request.form['password']):
                fuser = FlaskUser()
                fuser.email = email
                fuser.id = user.id
                fuser.username = user.username
                flask_login.login_user(fuser)
                logging.debug('Logged in successfully.')
                flash('Logged in successfully.')
                return redirect(url_for('index'))
            else:
                logging.debug('Wrong password.')
                flash('Wrong password.')
                return redirect(url_for('login'))
        except Exception as e:
            logging.warn(e)
            return "User not exist."
    else:
        return current_app.send_static_file('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if not username or not password or not email:
            return 'Input not valid.'
        try:
            user = User.objects(email=email).get()
        except Exception:
            user = User(username=username, password=bcrypt.generate_password_hash(password), email=email)
            user.save()
            return 'Success.'
        else:
            return 'Already exists.'
    else:
        return current_app.send_static_file('register.html')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))

@app.route('/checklogin')
def check_login():
    if flask_login.current_user.is_authenticated:
        return json.dumps({
            "login": True,
            "username": flask_login.current_user.username
        })
    else:
        return json.dumps({
            "login": False,
        })

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
    page = int(request.args.get('page', ''))

    search = SearchLog.create(keyword=keyword, user=str(flask_login.current_user.id))
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

    logging.debug("Order by : " + request.args.get('order_by', ''))
    if request.args.get('order_by', '') == "Default":
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

    if request.args.get('order_by', '') == "Publication Date(Ascending)":
        query_result.papers_array.sort(key=lambda x: x["ParsedDate"])

    if request.args.get('order_by', '') == "Publication Date(Descending)":
        query_result.papers_array.sort(key=lambda x: x["ParsedDate"], reverse=True)

    logging.debug("Filter by : " + request.args.get('filter_by', ''))

    if request.args.get('filter_by', '')!="Default":
        return_list = [paper for paper in query_result.papers_array if paper["Abstract"].lower().find(request.args.get('filter_by', '')) != -1]
    else:
        return_list = query_result.papers_array

    bag = AbstractProcessor().process_list(return_list)
    words = [[y, bag[y]] for y in sorted(list(bag.keys()), key=lambda x: bag[x], reverse=True)[:30]]

    return_value = json.dumps(
        {
            "success": True,
            "errors": [],
            "result": return_list[(page-1)*RESULTS_PER_PAGE:page*RESULTS_PER_PAGE],
            "result_info": {
                "page": math.ceil(len(return_list)/RESULTS_PER_PAGE),
                "count": len(return_list),
                "id": search.id,
                "failure_pubmed": query_result.failure_pubmed,
                "words": words
            }
        }
    )
    return return_value

@app.route('/jump/<int:search_id>/<int:paper_id>')
def jump(search_id, paper_id):
    if search_id in search_id_to_results:
        query = search_id_to_results[search_id]
        try:
            # pylint: disable=E1101
            search_term_text = SearchLog.get(SearchLog.id == search_id).keyword
            # pylint: enable=E1101
            local_search_term = SearchTerm.get(SearchTerm.keyword == search_term_text)
        except:
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
            click, created = Click.get_or_create(search_term=local_search_term, paper=local_paper)
            if paper_id == i:
                # pylint: disable=E1101
                click.click_count += 1
                # pylint: enable=E1101
                click.save()
        return redirect(
            query.papers_array[paper_id]["URL"]
        )
    else:
        abort(404)

@app.route('/instant/<keyword>')
def instant_search(keyword):
    keyword = keyword.replace("%20", "")
    with app.app_context():
        return json.dumps(list(map(lambda b: b.decode('utf-8'), instant.search(keyword)))[:20])

@app.route('/subscription/add/<keyword>')
def add_subscription(keyword):
    try:
        Subscription.add(keyword)
        return 'ok'
    except:
        return 'error'

@app.route('/subscription/timeline')
def timeline():
    papers = Subscription.get_timeline()
    return json.dumps([{'title': x.title, 'date': x.date.strftime("%Y-%m-%d"), 'authors': [a.name for a in x.authors], 'url': x.url} for x in papers])

@app.route('/subscription/recommendations')
def recommendations():
    pass

class FlaskUser(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    try:
        user = User.objects(email=email).get()
    except:
        return None
    fuser = FlaskUser()
    fuser.email = email
    fuser.id = user.id
    fuser.username = user.username
    return fuser

# if __name__ == '__main__':
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')
results = {}
search_id_to_results = {}
instant = InstantSearch()
app.secret_key = 'test'
app.debug = True


