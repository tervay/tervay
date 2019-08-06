from flask import render_template, redirect, flash, get_flashed_messages

from app import app
from webpy.manager import all_items

for item in all_items:
    url = str(item.url).lstrip('/')


    def create(item_embedded):
        """Create anonymous inner function in order to avoid namespace clashing"""

        def temporary():
            form_class = item_embedded.fn.generate_flask_form()
            form = form_class()
            if form.validate_on_submit():
                fn_args = []
                for arg_name, form_field in vars(form).items():
                    if arg_name in [p.name for p in item_embedded.fn.signature.parameters.values()]:
                        fn_args.append(form_field.data)

                flash(item_embedded.fn.fn(*fn_args))
                return redirect(f'/share/{url}')

            fields = []
            for arg_name, form_field in vars(form).items():
                if arg_name in [p.name for p in item_embedded.fn.signature.parameters.values()] or arg_name == 'submit':
                    fields.append((arg_name, form_field))
            return render_template('py_function.html', **{
                'item': item_embedded,
                'form': form,
                'form_fields': fields,
                'form_vars': vars(form),
                'msgs': get_flashed_messages()
            })

        return temporary


    # Ew
    vars()[f'route_for_{item.name}'] = create(item)
    vars()[f'route_for_{item.name}'].__name__ = f'route_for_{item.name}'
    vars()[f'route_for_{item.name}'] = app.route(f'/share/{url}', methods=['GET', 'POST'])(
        vars()[f'route_for_{item.name}'])
    print(f'Bound {url} to {vars()[f"route_for_{item.name}"]}')
