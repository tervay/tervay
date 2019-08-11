# noinspection PyUnresolvedReferences
import models
# noinspection PyUnresolvedReferences
import routing
# noinspection PyUnresolvedReferences
import webpy.start
from app import app


# Live template reloading
@app.before_request
def clear_cache():
    app.jinja_env.cache = {}
