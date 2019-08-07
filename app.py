import os

from flask import Flask
from flask_sslify import SSLify

from tbapy import TBA

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('CSRF_KEY') or 'testing-string'
SSLify(app, subdomains=True)

tba = TBA(os.environ.get('TBA_KEY'))
