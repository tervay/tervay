import inspect
from collections import namedtuple
from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import IntegerField, DecimalField
from wtforms.validators import DataRequired

Item = namedtuple('Item', ['name', 'url', 'fn'])
all_items = []  # type: List[Item]

type_to_field = {
    int: IntegerField,
    str: StringField,
    Decimal: DecimalField
}


class FunctionDescriptor:
    def __init__(self, fn):
        self.fn = fn
        signature = inspect.signature(self.fn)
        self.signature = signature

    def generate_flask_form(self):
        form_cls = type(f'{self.fn.__name__}Form', (FlaskForm,), {
            **{p.name: type_to_field.get(p.annotation, StringField)(p.name, validators=[DataRequired()])
               for p in self.signature.parameters.values()},
            **{'submit': SubmitField('Submit')}
        })
        return form_cls


def expose(name, url):
    def wrap(fn):
        global all_items
        all_items.append(Item(name=name, url=url, fn=FunctionDescriptor(fn)))
        return fn

    return wrap
