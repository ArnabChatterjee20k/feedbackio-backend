import os
from flask import Flask,request
from werkzeug.exceptions import Forbidden
from flask_cors import CORS
from api.utils import is_valid_request
from api.db import create_models

def create_api():
    app = Flask(__name__)
    hosted_app_url = os.environ.get("APP_URL")
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost", "http://127.0.0.1", hosted_app_url]
        }
    })

    from .permissions import permission_router
    app.register_blueprint(permission_router)
    
    @app.get("/")
    def health_check():
        return "Running great", 200

    create_models()
    @app.before_request
    def check_validity():
        endpoint = request.endpoint
        # function name
        if endpoint in ["health_check"]:
            return
        if is_valid_request():
            return
        return Forbidden()
    return app