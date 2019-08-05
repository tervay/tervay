import os

from pony.orm import Database

# noinspection PyUnresolvedReferences
from app import app

db = Database()
db.bind(provider='postgres',
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_DATABASE'),
        user=os.environ.get('DB_USER'),
        port=5432,
        password=os.environ.get('DB_PASSWORD'))

# noinspection PyUnresolvedReferences
import models
# noinspection PyUnresolvedReferences
import routing

db.generate_mapping(create_tables=False)
