import os
from flask import Flask
from flask_cors import CORS

def create_api():
    app = Flask(__name__)
    hosted_app_url = os.environ.get("APP_URL")
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost", "http://127.0.0.1", hosted_app_url]
        }
    })
    @app.get("/")
    def health_check():
        return "Running great", 200

    return app
