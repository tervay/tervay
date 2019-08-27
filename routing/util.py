from app import app

from util import download


# @app.route("/util/download/")
def download_view():
    fns = [download.download_event_teams]

    s = []
    for fn in fns:
        fn()
        s.append(fn.__name__)

    return f'Called: {", ".join(s)}'
