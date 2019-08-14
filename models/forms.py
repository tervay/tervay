import hashlib
import os

from flask_admin.contrib.pymongo import ModelView
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class HotlinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create')

    def validate_password(self, field):
        salt = os.environ.get('SALT')
        digest = os.environ.get('AUTH')
        hashed = hashlib.sha512((field.data + salt).encode()).hexdigest()
        if hashed != digest:
            raise ValidationError('Password does not match')


class HotlinkView(ModelView):
    column_list = ('name', 'url')
    can_delete = False
    form = HotlinkForm
