import hashlib
import os

from flask import render_template, flash, get_flashed_messages
from pony.orm import db_session
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from app import app
from models.database import Hotlink
from models.forms import HotlinkForm


@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/linker/', methods=['GET', 'POST'])
@db_session
def linker():
    form = HotlinkForm()
    show = []
    if 'show_hotlinks' in get_flashed_messages():
        show = [(h.name, h.url) for h in Hotlink.select(lambda h: True)]
    if form.validate_on_submit():
        pw = form.password.data
        name = form.name.data
        url = form.url.data
        debug = app.config['SECRET_KEY'] == 'testing-string'
        if debug:
            if name == 'show':
                print('flashing')
                flash('show_hotlinks')
            else:
                print('create')
                Hotlink(name=name, url=url)
            return redirect('/linker')

        salt = os.environ.get('SALT')
        digest = os.environ.get('AUTH')
        hashed = hashlib.sha512((pw + salt).encode()).hexdigest()
        if hashed == digest:
            if name == 'show':
                print('flashing')
                flash('show_hotlinks')
            else:
                print('create')
                Hotlink(name=name, url=url)
            return redirect('/linker')
        else:
            abort(403)

    return render_template('hotlink_form.html', form=form, show=show)


@app.route('/<path:shortlink>/')
@db_session
def fallback(shortlink):
    query = Hotlink.select(lambda l: l.name == shortlink)
    if query.exists():
        return redirect(query.first().url)
    else:
        abort(404)
