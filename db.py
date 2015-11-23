from peewee import *
import datetime

database = SqliteDatabase('my_database.db', threadlocals=True)


class BaseModel(Model):
    class Meta:
        database = database


class Search(BaseModel):
    keyword = TextField()
    date = DateTimeField(default=datetime.datetime.now)


class Visit(BaseModel):
    search = ForeignKeyField(Search, related_name='visits')
    title = TextField()
    citations = IntegerField(default=-1)
    year = IntegerField(null=True)
    authors = TextField(null=True)
    last_author = TextField(null=True)
    journal = TextField(null=True)
    journalif = FloatField(default=0)
    score = FloatField(default=0)
    date = DateTimeField(default=datetime.datetime.now)
    completed = BooleanField(default=False)

database.connect()
Search.create_table(True)
Visit.create_table(True)
database.close()
