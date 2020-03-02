from collections import defaultdict

from flask import render_template

from app import app
from webpy.manager import all_items


@app.route("/share/")
def list_all():
    d = defaultdict(dict)
    for item in all_items:
        d[item.group][item] = [
            (arg.name, arg.get_native_type().__name__) for arg in item.arguments
        ]

    return render_template("py_function_list.html.jinja2", **{"data": d})
