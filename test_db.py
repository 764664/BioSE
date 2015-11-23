from peewee import *
import datetime

db = SqliteDatabase('my_database.db', threadlocals=True)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)


class Tweet(BaseModel):
    user = ForeignKeyField(User, related_name='tweets')
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
    is_published = BooleanField(default=True)

db.connect()
User.create_table(True)
Tweet.create_table(True)
charlie = User.create(username='charlie')
huey = User(username='huey')
huey.save()
Tweet.create(user=charlie, message='My first tweet')
