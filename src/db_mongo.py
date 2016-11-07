from mongoengine import *
import datetime

connect('biose')

class Author(Document):
    name = StringField()

class Paper(Document):
    title = StringField()
    authors = ListField(ReferenceField(Author))
    abstract = StringField()
    journal = StringField()
    date = DateTimeField()
    url = StringField()
    subscriptions = ListField(ReferenceField('SubscriptionItem'))

class SubscriptionItem(Document):
    keyword = StringField()
    papers = ListField(ReferenceField(Paper))

class User(Document):
    username = StringField()
    password = StringField()
    email = StringField()
    subscriptions = ListField(ReferenceField(SubscriptionItem))

class SearchItem(Document):
    keyword = StringField()
    count = IntField()
    model = BinaryField()

class SearchHistory(Document):
    item = ReferenceField(SearchItem)
    user = ReferenceField(User)
    time = DateTimeField(default=datetime.datetime.now)