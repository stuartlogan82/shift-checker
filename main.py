from flask import Flask, render_template
from flask_cors import CORS
import connexion
import os

app = connexion.App(__name__, specification_dir="./")

app.add_api('swagger.yml')
CORS(app.app)

@app.route('/')
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
