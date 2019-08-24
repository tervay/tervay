from flask import render_template

from app import app
from webpy.manager import all_items
from collections import defaultdict


@app.route("/share/")
def list_all():
    d = defaultdict(dict)
    for item in all_items:
        d[item.group][item] = [
            (arg, item.get_casted_type_for_attr(arg).__name__)
            for arg in item.get_arg_names()
        ]

    return render_template("py_function_list.html.jinja2", **{"data": d})
