import inspect
import json
import traceback
from decimal import Decimal
from enum import Enum, auto
from inspect import Parameter
from typing import List

from flask import get_flashed_messages, jsonify, render_template, request
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import DecimalField, IntegerField
from wtforms.validators import DataRequired

from cache import purge_frame_cache
from codegen import codegen

all_items = []  # type: List[FunctionDescriptor]

type_to_field = {int: IntegerField, str: TextAreaField, Decimal: DecimalField}


class Group(Enum):
    FRC = auto()
    League_of_Legends = auto()
    etc = auto()

    def to_label(self):
        return self.name.replace("_", " ").upper()


class Type(Enum):
    int = auto()
    string = auto()
    float = auto()
    text = auto()
    json = auto()


class RenderAs(Enum):
    text = auto()
    table = auto()


class Argument:
    def __init__(self, parameter: Parameter):
        self.parameter = parameter
        self.name = parameter.name
        self.type = parameter.annotation

    def get_native_type(self):
        return {
            Type.int: int,
            Type.string: str,
            Type.float: Decimal,
            Type.text: str,
            Type.json: str,
        }[self.type]

    def get_form_field(self):
        return {
            Type.int: IntegerField,
            Type.string: StringField,
            Type.float: DecimalField,
            Type.text: TextAreaField,
            Type.json: TextAreaField,
        }[self.type]

    def get_html_field(self):
        return {
            Type.int: "forms/int_field.html.jinja2",
            Type.string: "forms/string_field.html.jinja2",
        }[self.type]


class FunctionDescriptor:
    def __init__(self, name, url, fn, group, render_as):
        self.name = name
        self.url = url
        self.fn = fn
        self.group = group
        self.arguments = [
            Argument(p) for p in inspect.signature(self.fn).parameters.values()
        ]
        self.render_as = render_as

    def get_argument(self, name: str) -> Argument:
        for a in self.arguments:
            if a.name == name:
                return a

        return None

    def get_render_template(self):
        return {
            RenderAs.text: "renderers/text.html.jinja2",
            RenderAs.table: "renderers/table.html.jinja2",
        }[self.render_as]

    def generate_flask_form(self):
        form_cls = type(
            f"{self.fn.__name__}Form",
            (FlaskForm,),
            {
                **{
                    a.name: a.get_form_field()(a.name, validators=[DataRequired()])
                    for a in self.arguments
                },
                **{"submit": SubmitField("Submit"), "refresh": BooleanField("Refresh")},
            },
        )
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
            fields = [(a.name, getattr(form, a.name)) for a in self.arguments] + [
                ("submit", form.submit),
                ("refresh", form.refresh),
            ]

            context = {
                "item": self,
                "form": form,
                "form_fields": fields,
                "form_vars": vars(form),
                "msgs": get_flashed_messages(),
                "api_endpoint": f"/share/{self.url}_json/",
                "fields": [
                    render_template(a.get_html_field(), label=a.name, id=a.name)
                    for a in self.arguments
                ],
            }

            # noinspection PyArgumentList
            return render_template("py_function.html.jinja2", **context)

        return temporary

    def create_flask_json_endpoint(self):
        def temporary():
            if request.method == "POST":
                try:
                    fn_args = {}
                    request_data = json.loads(request.data)
                    for arg in self.arguments:
                        val = request_data[arg.name]
                        casted = arg.get_native_type()(val)
                        fn_args[arg.name] = casted

                    if "refresh" in request_data and request_data["refresh"]:
                        purge_frame_cache(self.fn, **fn_args)
                    result, cache_hit = self.fn(**fn_args)
                    if "raw" not in request_data:
                        return jsonify(
                            {
                                "result": render_template(
                                    self.get_render_template(), result=result
                                ),
                                "cached": cache_hit,
                            }
                        )
                    else:
                        return jsonify({"result": result, "cached": cache_hit})

                except Exception as e:
                    return jsonify({"error": f"{str(e)}: {traceback.format_exc()}"})

            return jsonify({"error": "must be a POST request"})

        return temporary

    def create_source_endpoint(self):
        def temporary():
            context = {
                "source_code": codegen.get_generated_network_code(self),
                "name": self.fn.__name__,
            }

            return render_template("py_function_source.html.jinja2", **context)

        return temporary


def expose(name, url, group, render_as):
    def wrap(fn):
        global all_items
        all_items.append(
            FunctionDescriptor(
                name=name, url=url, fn=fn, group=group, render_as=render_as
            )
        )
        return fn

    return wrap
