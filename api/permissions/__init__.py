from flask import Blueprint
permission_router = Blueprint("PermissionRouter",__name__,url_prefix="/permissions")

from . import routes