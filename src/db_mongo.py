from mongoengine import *

connect('biose')

class Author(Document):
    name = StringField()

class Paper(Document):
    title = StringField()
    authors = ListField(ReferenceField(Author))
    abstract = StringField()
    journal = StringField()
    date = DateTimeField()

class SubscriptionItem(Document):
    keyword = StringField()
    papers = ListField(ReferenceField(Paper))

class User(Document):
    username = StringField()
    password = StringField()
    email = StringField()
    subscriptions = ListField(ReferenceField(SubscriptionItem))