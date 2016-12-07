from mongoengine import *
from mongoengine import signals
import datetime
import flask_login
import logging

connect('biose')

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
    meta = {
        'indexes': [
            'name'
        ]
    }

class Paper(MyDocument):
    title = StringField()
    authors = ListField(ReferenceField(Author))
    abstract = StringField()
    journal = StringField()
    date = DateTimeField()
    url = StringField()
    subscriptions = ListField(ReferenceField('SubscriptionItem'))
    meta = {
        'indexes': [
            'title'
        ]
    }

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
    category = StringField()
    pointer = GenericReferenceField()
    papers = ListField(ReferenceField(Paper))

    def serialize(self):
        return({'keyword': self.keyword, 'id': str(self.id)})

class User(MyDocument, flask_login.UserMixin):
    username = StringField()
    password = StringField()
    email = StringField()
    subscriptions = ListField(ReferenceField(SubscriptionItem))

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
    namespace = StringField()
    # For GoTerm, it's the oid of ancestor
    # For MeSH Term, it's the numbers of itself
    tree_number_list = ListField(StringField())
    oid = StringField()
    ancestors = ListField(ReferenceField('self'))
    synonyms = ListField(StringField())
    cached_json = StringField()
    meta = {
        'indexes': [
            'oid',
            'tree_number_list',
            'name',
            'source'
        ]
    }

    def serialize(self):
        # ancestors_all = []
        # ancestors = self.ancestors
        # while ancestors:
        #     ancestors_all.append([(ancestor.) for ancestor in ancestors
        return(
            {
                'name': self.name,
                'source': self.source,
                'definition': self.definition,
                'namespace': self.namespace,
                'id': str(self.id),
                'synonyms': self.synonyms,
                'oid': self.oid
                # 'ancestors': [ancestor.serialize() for ancestor in self.ancestors] if self.ancestors else None
            }
        )

signals.pre_save.connect(update_modified)
