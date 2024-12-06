from dotenv import load_dotenv
load_dotenv(".env")
from api import create_api

app = create_api()

if __name__ == "__main__":
    app.run(debug=True)