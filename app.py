import logging
import os

import sentry_sdk
from flask import Flask
from flask_admin import Admin
from flask_sslify import SSLify
from sentry_sdk.integrations.flask import FlaskIntegration
from tbapy import TBA

from models.database import db
from models.forms import HotlinkView

tba = TBA(os.environ.get("TBA_KEY"))
app = Flask(__name__, template_folder="templates")
app.config["SECRET_KEY"] = os.environ.get("CSRF_KEY") or "testing-string"

# Auto https
SSLify(app, subdomains=True)

# Add /admin url
admin = Admin(app)
admin.add_view(HotlinkView(db["hotlinks"]))

# Sentry
sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN"), integrations=[FlaskIntegration()])

# Logging
logFormatter = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(format=logFormatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Live template reloading
@app.before_request
def clear_cache():
    app.jinja_env.cache = {}


# Bring URLs into scope
# noinspection PyUnresolvedReferences
import routing

# noinspection PyUnresolvedReferences
import webpy
