from flask import render_template
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from app import app
from models.database import hotlinks


@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/<path:shortlink>/')
def fallback(shortlink):
    query = hotlinks.find_one({'name': shortlink})
    if query is not None:
        return redirect(query['url'])
    else:
        abort(404)
