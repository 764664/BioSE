import json
import logging
import math

import flask_login
from flask import current_app, redirect, g, abort, request, url_for, flash
from flask_bcrypt import Bcrypt

from src import app
from src.controllers.search_controller import SearchController
from src.db import SearchLog, SearchTerm, Click, Paper, database
from src.helpers.autocomplete import InstantSearch
from src.models.schema import User
from src.models.subscription import Subscription

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
            logging.warning(e)
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
            fuser = FlaskUser()
            fuser.email = email
            fuser.id = user.id
            fuser.username = user.username
            flask_login.login_user(fuser)
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
        logging.info("Authenticated.")
        return json.dumps({
            "login": True,
            "username": flask_login.current_user.username
        })
    else:
        logging.info("Not authenticated.")
        return json.dumps({
            "login": False,
        })

@app.route('/search/<keyword>')
def search(keyword):
    with app.app_context():
        return SearchController.search(keyword, request.args)

@app.route('/fetch')
def fetch():
    with app.app_context():
        return SearchController.fetch(request.args)


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
def subscription_add(keyword):
    try:
        Subscription.add(keyword)
        return 'ok'
    except:
        return 'error'

@app.route('/subscription/timeline')
def subscription_timeline():
    count = request.args.get('count', 20)
    offset = int(request.args.get('offset', 0))

    papers = Subscription.get_timeline()
    if offset > len(papers):
        return json.dumps({'response': [], 'more':False})
    else:
        more = offset+count < len(papers)
        papers = papers[offset: offset+count]
        return json.dumps({'response':[{'title': x.title, 'date': x.date.strftime("%Y-%m-%d"), 'journal': x.journal, 'authors': [a.name for a in x.authors], 'url': x.url, 'subscriptions': [s.keyword for s in x.subscriptions]} for x in papers],
        'more': more})

@app.route('/subscription/index')
def subscription_index():
    subscriptions = Subscription.index()
    return json.dumps([{'keyword': x.keyword} for x in subscriptions])

@app.route('/subscription/recommendations')
def subscription_recommendations():
    pass

class FlaskUser(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(id):
    logging.debug("User loader:{}".format(id));
    try:
        user = User.objects(id=id).get()
    except:
        return None
    fuser = FlaskUser()
    fuser.email = user.email
    fuser.id = id
    fuser.username = user.username
    return fuser

# if __name__ == '__main__':
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')

instant = InstantSearch()
app.secret_key = 'test'


