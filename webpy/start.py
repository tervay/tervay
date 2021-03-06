from app import app
from webpy.manager import all_items

for item in all_items:
    url = str(item.url).strip("/")
    item.url = url
    # Ew
    route_name = f"route_for_{item.name}"
    vars()[route_name] = item.create_flask_route_function()
    vars()[route_name].__name__ = route_name
    vars()[route_name] = app.route(f"/share/{url}/", methods=["GET", "POST"])(
        vars()[route_name]
    )

    json_endpoint = f"{route_name}_json"
    vars()[json_endpoint] = item.create_flask_json_endpoint()
    vars()[json_endpoint].__name__ = json_endpoint
    vars()[json_endpoint] = app.route(f"/share/{url}_json/", methods=["GET", "POST"])(
        vars()[json_endpoint]
    )

    source_endpoint = f"{route_name}_source"
    vars()[source_endpoint] = item.create_source_endpoint()
    vars()[source_endpoint].__name__ = source_endpoint
    vars()[source_endpoint] = app.route(
        f"/share/{url}/source/", methods=["GET", "POST"]
    )(vars()[source_endpoint])
