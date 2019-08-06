from flask import render_template, redirect, flash, get_flashed_messages

from app import app
from webpy.manager import all_items

for item in all_items:
    url = str(item.url).lstrip('/')
    form_class = item.fn.generate_flask_form()


    @app.route(f'/share/{url}', methods=['GET', 'POST'])
    def _():
        form = form_class()
        if form.validate_on_submit():
            fn_args = []
            for arg_name, form_field in vars(form).items():
                if arg_name in [p.name for p in item.fn.signature.parameters.values()]:
                    fn_args.append(form_field.data)

            flash(item.fn.fn(*fn_args))
            return redirect(f'/share/{url}')

        fields = []
        for arg_name, form_field in vars(form).items():
            if arg_name in [p.name for p in item.fn.signature.parameters.values()] or arg_name == 'submit':
                fields.append((arg_name, form_field))
        return render_template('py_function.html', **{
            'item': item,
            'form': form,
            'form_fields': fields,
            'form_vars': vars(form),
            'msgs': get_flashed_messages()
        })
