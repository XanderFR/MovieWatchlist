import os
from flask import Flask
from pymongo import MongoClient

from routes import pages


app = Flask(__name__)
app.register_blueprint(pages)
client = MongoClient("mongodb://localhost:27017")
app.db = client.moviewatchlist

app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "$3cR3t_K3y"
    )

if __name__ == "__main__":
    app.run(debug=True)
