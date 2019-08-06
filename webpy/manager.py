import inspect
import json
from decimal import Decimal
from typing import List

from flask import get_flashed_messages, jsonify, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import DecimalField, IntegerField
from wtforms.validators import DataRequired

all_items = []  # type: List[FunctionDescriptor]

type_to_field = {
    int:     IntegerField,
    str:     StringField,
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
            **{p.name: type_to_field.get(p.annotation, StringField)(
                p.name, validators=[DataRequired()])
                for p in self.signature.parameters.values()},
            **{'submit': SubmitField('Submit')}
        })
        return form_cls

    def create_flask_route_function(self):
        """Create anonymous inner function in order to avoid namespace
        clashing"""

        def temporary():
            """
            Routing function
            """
            form_class = self.generate_flask_form()
            form = form_class()
            fields = [(a, getattr(form, a)) for a in self.get_arg_names()] + \
                     [('submit', form.submit)]
            return render_template('py_function.html', **{
                'item':         self,
                'form':         form,
                'form_fields':  fields,
                'form_vars':    vars(form),
                'msgs':         get_flashed_messages(),
                'api_endpoint': f'/share/{self.url}_json/'
            })

        return temporary

    def create_flask_json_endpoint(self):
        def temporary():
            if request.method == 'POST':
                try:
                    fn_args = []
                    for arg_name in self.get_arg_names():
                        value = json.loads(request.data)[arg_name]
                        casted = self.get_type_for_attr(arg_name)(value)
                        fn_args.append(casted)
                    return jsonify({'result': str(self.fn(*fn_args))})
                except Exception as e:
                    print(e)
                    return jsonify({'error': str(e)})

            return jsonify({'error': 'must be a POST request'})

        return temporary

    def get_arg_names(self):
        form_class = self.generate_flask_form()
        form = form_class()
        fn_args = []
        for arg_name, form_field in vars(form).items():
            if arg_name in [p.name for p in self.signature.parameters.values()]:
                fn_args.append(arg_name)
        return fn_args

    def get_type_for_attr(self, attr: str):
        return self.signature.parameters[attr].annotation


def expose(name, url):
    def wrap(fn):
        global all_items
        all_items.append(FunctionDescriptor(name=name, url=url, fn=fn))
        return fn

    return wrap
