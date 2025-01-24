from dotenv import load_dotenv
import os
load_dotenv(".env")
from app import create_app
app = create_app()
# app.config["DEBUG"] = bool(os.environ.get("PROD")!="1")