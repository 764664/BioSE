from mongoengine import *
from mongoengine import signals
import datetime
import flask_login
from src import app
import logging

connect('biose')
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

def update_modified(sender, document):
    document.modified_at = datetime.datetime.utcnow()

class MyDocument(Document):
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    modified_at = DateTimeField()

    meta = {
        'abstract': True,
    }

class Author(MyDocument):
    name = StringField()

class Journal(MyDocument):
    name = StringField()
    impact_factor = FloatField()
    eigenfactor_score = FloatField()

class Paper(MyDocument):
    title = StringField()
    authors = ListField(ReferenceField(Author))
    abstract = StringField()
    journal = StringField()
    date = DateTimeField()
    url = StringField()
    subscriptions = ListField(ReferenceField('SubscriptionItem'))


    def serialize(self):
        return(
            {
                'title': self.title,
                'abstract': self.abstract,
                'url': self.url,
                'date': self.date.strftime("%Y-%m-%d"),
                'journal': self.journal,
                'authors': [author.name for author in self.authors],
                'id': str(self.id),
                'subscriptions': [sub.keyword for sub in self.subscriptions]
            }
        )

class SubscriptionItem(MyDocument):
    keyword = StringField()
    papers = ListField(ReferenceField(Paper))


class User(MyDocument, flask_login.UserMixin):
    username = StringField()
    password = StringField()
    email = StringField()
    subscriptions = ListField(ReferenceField(SubscriptionItem))

@login_manager.user_loader
def user_loader(id):
    logging.debug("User loader:{}".format(id));
    return User.objects(id=id).get()

class SearchItem(MyDocument):
    keyword = StringField()
    count = IntField(default=0)
    model = BinaryField()
    papers = ListField(ReferenceField(Paper))


class SearchHistory(MyDocument):
    item = ReferenceField(SearchItem)
    user = ReferenceField(User)
    papers = ListField(ReferenceField(Paper))


class ClickCount(MyDocument):
    search_item = ReferenceField(SearchItem)
    paper = ReferenceField(Paper)
    count = IntField(default=0)


class ClickHistory(MyDocument):
    search_item = ReferenceField(SearchItem)
    search_history = ReferenceField(SearchHistory)
    paper = ReferenceField(Paper)
    user = ReferenceField(User)

class Term(MyDocument):
    name = StringField()
    source = StringField()
    definition = StringField()
    tree_number_list = ListField(StringField())
    oid = StringField()

signals.pre_save.connect(update_modified)
