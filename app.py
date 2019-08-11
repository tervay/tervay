import os

from flask import Flask
from flask_admin import Admin
from flask_sslify import SSLify
from tbapy import TBA

from models.database import db
from models.forms import HotlinkView

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('CSRF_KEY') or 'testing-string'
SSLify(app, subdomains=True)
admin = Admin(app)
admin.add_view(HotlinkView(db['hotlinks']))

tba = TBA(os.environ.get('TBA_KEY'))
