import os

from pymongo import MongoClient

client = MongoClient(os.environ.get('MONGODB_URI'))
db = client[os.environ.get('MONGODB_URI').split('/')[-1]]
hotlinks = db['hotlinks']
