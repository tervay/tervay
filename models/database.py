from pony.orm import Required

from start import db


class Hotlink(db.Entity):
    name = Required(str)
    url = Required(str)
