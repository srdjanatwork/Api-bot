# -*- coding: utf-8 -*-
from os import environ

from pymongo import MongoClient

db_url = environ['MONGO_URL']
client = MongoClient(db_url)
db = client.get_database(environ.get('MONGO_DATABASE', 'undefined_database_env_var'))
