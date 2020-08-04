from flask import Flask, render_template
import connexion
import os

app = connexion.App(__name__, specification_dir="./")

app.add_api('swagger.yml')


def basic_auth(username, password, required_scopes=None):
    if username == os.environ.get("API_USERNAME") and password == os.environ.get("API_PASSWORD"):
        return {'Auth', 'OK'}

    return None


@app.route('/')
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'), debug=True)
