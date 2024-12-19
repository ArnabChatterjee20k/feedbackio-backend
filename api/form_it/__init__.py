from flask import Blueprint
form_it_router = Blueprint("FormItRouter",__name__,url_prefix="/form")

from . import routes
from . import model