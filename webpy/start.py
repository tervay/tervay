from app import app
from webpy.manager import all_items

for item in all_items:
    url = str(item.url).strip('/')

    # Ew
    vars()[f'route_for_{item.name}'] = item.create_flask_route_function()
    vars()[f'route_for_{item.name}'].__name__ = f'route_for_{item.name}'
    vars()[f'route_for_{item.name}'] = app.route(f'/share/{url}/', methods=['GET', 'POST'])(
        vars()[f'route_for_{item.name}'])
