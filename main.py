from dotenv import load_dotenv
import os
load_dotenv(".env")
from api import create_api
app = create_api()
app.config["DEBUG"] = bool(os.environ.get("PROD")!="1")
if __name__ == "__main__":
    app.run()