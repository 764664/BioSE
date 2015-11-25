from peewee import *
import datetime

database = SqliteDatabase('my_database.db', threadlocals=True)


class BaseModel(Model):
    class Meta:
        database = database


class SearchTerm(BaseModel):
    keyword = TextField()


class SearchLog(BaseModel):
    keyword = TextField()
    date = DateTimeField(default=datetime.datetime.now)


class Paper(BaseModel):
    title = TextField()
    citations = IntegerField(default=-1)
    year = IntegerField(null=True)
    authors = TextField(null=True)
    last_author = TextField(null=True)
    journal = TextField(null=True)
    journal_if = FloatField(default=0)
    # score = FloatField(default=0)
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

print("Starting Execution.")
database.connect()
SearchTerm.create_table(True)
SearchLog.create_table(True)
Paper.create_table(True)
Click.create_table(True)
Model.create_table(True)
Journal.create_table(True)
database.close()
print("Finishing Execution.")