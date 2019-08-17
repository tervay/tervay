import inspect
import json
import traceback
from decimal import Decimal

from flask import get_flashed_messages, jsonify, render_template, request
from flask_wtf import FlaskForm
from typing import List
from wtforms import BooleanField, StringField, SubmitField
from wtforms.fields.html5 import DecimalField, IntegerField
from wtforms.validators import DataRequired

from cache import purge_frame_cache

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
            **{
                'submit':  SubmitField('Submit'),
                'refresh': BooleanField('Refresh')
            }
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
                     [('submit', form.submit), ('refresh', form.refresh)]
            context = {
                'item':         self,
                'form':         form,
                'form_fields':  fields,
                'form_vars':    vars(form),
                'msgs':         get_flashed_messages(),
                'api_endpoint': f'/share/{self.url}_json/'
            }
            # noinspection PyArgumentList
            return render_template('py_function.html', **context)

        return temporary

    def create_flask_json_endpoint(self):
        def temporary():
            if request.method == 'POST':
                try:
                    fn_args = {}
                    request_data = json.loads(request.data)
                    for arg_name in self.get_arg_names():
                        value = request_data[arg_name]
                        casted = self.get_type_for_attr(arg_name)(value)
                        fn_args[arg_name] = casted

                    if request_data['refresh']:
                        purge_frame_cache(self.fn, **fn_args)

                    result, cache_hit = self.fn(**fn_args)
                    return jsonify(
                        {
                            'result': json.dumps(result, indent=4,
                                                 sort_keys=True),
                            'cached': cache_hit
                        }
                    )
                except Exception as e:
                    return jsonify(
                        {'error': f'{str(e)}: {traceback.format_exc()}'})

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
