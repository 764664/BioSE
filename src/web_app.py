import json
import logging
import math

import flask_login
from flask import current_app, redirect, g, abort, request, url_for, flash, jsonify
from flask_bcrypt import Bcrypt

from src import app
from src.controllers.search_controller import SearchController
from src.controllers.paper_controller import PaperController
from src.helpers.autocomplete import InstantSearch
from src.models.schema import User
from src.models.subscription import Subscription
from IPython import embed

RESULTS_PER_PAGE = 10

bcrypt = Bcrypt(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def user_loader(id):
    logging.debug("User loader:{}".format(id));
    try:
        return User.objects(id=id).get()
    except:
        return None

# @app.before_request
# def before_request():
#     g.db = database
#     g.db.connect()
#
#
# @app.after_request
# def after_request(response):
#     g.db.close()
#     return response


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
                flask_login.login_user(user)
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
            flask_login.login_user(user)
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

@app.route('/search')
def search():
    with app.app_context():
        return SearchController.search(request.args)

@app.route('/fetch')
def fetch():
    with app.app_context():
        return SearchController.fetch(request.args)


@app.route('/jump')
def jump():
    with app.app_context():
        return SearchController.jump(request.args)

@app.route('/instant')
def instant_search():
    keyword = request.args.get('keyword')
    with app.app_context():
        # return json.dumps(list(map(lambda b: b.decode('utf-8'), instant.search(keyword)))[:20])
        return jsonify(response=InstantSearch.search(keyword))

@app.route('/subscription/add')
def add_subscription():
    return Subscription.add(request.args)

@app.route('/subscription/<id>', methods=['DELETE'])
def delete_subscription(id):
    return Subscription.delete(id)

@app.route('/subscription/timeline')
def subscription_timeline():
    count = request.args.get('count', 20)
    offset = int(request.args.get('offset', 0))

    papers = Subscription.get_timeline()
    if offset > len(papers):
        return jsonify(response=[], more=False)
    else:
        more = offset+count < len(papers)
        papers = papers[offset: offset+count]
        return jsonify(response=[paper.serialize() for paper in papers], more=more)

@app.route('/subscription/index')
def subscription_index():
    subscriptions = Subscription.index()
    return jsonify(response=[x.serialize() for x in subscriptions])

@app.route('/subscription/<id>')
def show_subscription(id):
    return Subscription.show(id)

@app.route('/subscription/recommend')
def subscription_recommendations():
    return Subscription.recommend()

@app.route('/paper/<id>')
def show_paper(id):
    return PaperController.show(id)

# if __name__ == '__main__':
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')

app.secret_key = 'test'


