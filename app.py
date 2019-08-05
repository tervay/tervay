import hashlib
import os

from flask import Flask, redirect, abort, render_template
from flask_wtf import FlaskForm
from pony.orm import Database, Required, set_sql_debug, db_session
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('CSRF_KEY') or 'testing-string'
db = Database()
db.bind(provider='postgres',
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_DATABASE'),
        user=os.environ.get('DB_USER'),
        port=5432,
        password=os.environ.get('DB_PASSWORD'))

debug = app.config['SECRET_KEY'] == 'testing-string'


class Hotlink(db.Entity):
    name = Required(str)
    url = Required(str)


class HotlinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create')


set_sql_debug(False)
db.generate_mapping(create_tables=True)


@app.route('/linker', methods=['GET', 'POST'])
@db_session
def linker():
    form = HotlinkForm()
    if form.validate_on_submit():
        pw = form.password.data
        name = form.name.data
        url = form.url.data
        if debug:
            Hotlink(name=name, url=url)
            return redirect('/')

        salt = os.environ.get('SALT')
        digest = os.environ.get('AUTH')
        hashed = hashlib.sha512((pw + salt).encode()).hexdigest()
        if hashed == digest:
            Hotlink(name=name, url=url)
            return redirect('/')
        else:
            abort(403)

    return render_template('hotlink_form.html', form=form)


@app.route('/<path:shortlink>')
@db_session
def fallback(shortlink):
    query = Hotlink.select(lambda l: l.name == shortlink)
    if query.exists():
        return redirect(query.first().url)
    else:
        abort(404)
