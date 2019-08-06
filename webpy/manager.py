import inspect
from decimal import Decimal
from typing import List

from flask import flash, redirect, render_template, get_flashed_messages
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import IntegerField, DecimalField
from wtforms.validators import DataRequired

all_items = []  # type: List[FunctionDescriptor]

type_to_field = {
    int: IntegerField,
    str: StringField,
    Decimal: DecimalField
}


class FunctionDescriptor:
    def __init__(self, name, url, fn):
        self.name = name
        self.url = url
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

    def create_flask_route_function(self):
        """Create anonymous inner function in order to avoid namespace clashing"""

        def temporary():
            """
            Routing function
            """
            form_class = self.generate_flask_form()
            form = form_class()
            if form.validate_on_submit():
                fn_args = []
                for arg_name, form_field in vars(form).items():
                    if arg_name in [p.name for p in self.signature.parameters.values()]:
                        fn_args.append(form_field.data)

                flash(self.fn(*fn_args))
                return redirect(f'/share/{self.url}')

            fields = []
            for arg_name, form_field in vars(form).items():
                if arg_name in [p.name for p in self.signature.parameters.values()] or arg_name == 'submit':
                    fields.append((arg_name, form_field))
            return render_template('py_function.html', **{
                'item': self,
                'form': form,
                'form_fields': fields,
                'form_vars': vars(form),
                'msgs': get_flashed_messages()
            })

        return temporary


def expose(name, url):
    def wrap(fn):
        global all_items
        all_items.append(FunctionDescriptor(name=name, url=url, fn=fn))
        return fn

    return wrap
