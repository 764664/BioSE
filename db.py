from peewee import *
import datetime
import logging

database = SqliteDatabase('my_database.db', threadlocals=True)

logger = logging.getLogger('peewee')
logger.setLevel(logging.INFO)

class BaseModel(Model):
    class Meta:
        database = database


class SearchTerm(BaseModel):
    keyword = CharField()


class SearchLog(BaseModel):
    keyword = CharField()
    date = DateTimeField(default=datetime.datetime.now)


class Paper(BaseModel):
    title = CharField()
    citations = IntegerField(default=-1)
    year = IntegerField(null=True)
    authors = CharField(null=True)
    last_author = CharField(null=True)
    journal = CharField(null=True)
    journal_if = FloatField(default=0)
    completed = BooleanField(default=False)
    last_modified = DateTimeField(default=datetime.datetime.now)


class Click(BaseModel):
    search_term = ForeignKeyField(SearchTerm, related_name='clicks')
    paper = ForeignKeyField(Paper, related_name='clicks')
    click_count = IntegerField(default=0)

class Model(BaseModel):
    search_term = ForeignKeyField(SearchTerm, related_name='model')
    model = BlobField()
    last_modified = DateTimeField(default=datetime.datetime.now)

class Journal(BaseModel):
    title = TextField()
    impact_factor = FloatField()
    eigenfactor_score = FloatField()

class Author(BaseModel):
    name = CharField()
    citations = IntegerField(null=True)
    h_index = IntegerField()
    i10_index = IntegerField(null=True)
    completed = BooleanField(default=False)

class InstantSearch(BaseModel):
    keyword = CharField(index=True)
    result = CharField()