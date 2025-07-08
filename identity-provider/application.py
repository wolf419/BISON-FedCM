from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from hashlib import sha256
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from bison import blindEval, get_signature, serialize_point_uncompressed, unserialize_point_uncompressed, verify_signature
import base64

from database import db, User
from sqlalchemy.exc import IntegrityError
import json

app = Flask(__name__)

app.secret_key = 'BAD_SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True
)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@login_required
def index():
    return render_template("index.html", name=current_user.username)

@app.route("/.well-known/web-identity")
def webid():
    with open(".well-known/web-identity") as file:
        data = json.load(file)
    return jsonify(data) 

@app.route("/config.json")
def config():
    with open("config.json") as file:
        data = json.load(file)
    return jsonify(data) 

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        user = User(username=username, email=email)
        user.set_password(password)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_template("signup.html", failed="Username or email already exist")

        return redirect(url_for("login"))

    else:
        return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for('index'))

        return render_template("login.html", failed="Wrong username or password")
    else:
        return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/auth/accounts")
@login_required
def accounts():
    # Verify the request contains `Sec-Fetch-Dest: webidentity`
    if request.headers.get("Sec-Fetch-Dest") != "webidentity":
        return jsonify({"error": "Invalid request"}), 400
    
    response = jsonify(current_user.get_dict())
    return response

@app.route("/auth/idtokens", methods=["POST"])
@login_required
def idtokens():
    # Verify the request contains `Sec-Fetch-Dest: webidentity`
    if request.headers.get("Sec-Fetch-Dest") != "webidentity":
        return jsonify({"error": "Invalid request"}), 400 
    
    account_id = request.form["account_id"]
    blinded_client_id_serialized = request.form["client_id"]

    # origin = request.headers.get("Origin")
    # if origin != client_id or str(current_user.id) != account_id:
    #     return jsonify({"error": "Invalid request"}), 400 

    blinded_client_id = unserialize_point_uncompressed(blinded_client_id_serialized)
    blinded_pseudonym = blindEval(blinded_client_id, int(current_user.user_id, 16))
    blinded_pseudonym_serialized = serialize_point_uncompressed(blinded_pseudonym)

    signature = get_signature(blinded_client_id_serialized + blinded_pseudonym_serialized)
    token = ".".join([base64.b64encode(signature).decode(), blinded_client_id_serialized, blinded_pseudonym_serialized])

    r = jsonify({"token": token})
    r.headers.set("Access-Control-Allow-Origin", request.headers.get("Origin"))
    r.headers.set("Access-Control-Allow-Credentials", "true")
    return r

# @app.after_request
# def log(response):
#     with open("log.txt", "a") as f:
#         f.write(request.method + " " + request.full_path + "\n")
#         f.write(request.headers.__str__())
#         f.write(request.form.__str__() + "\n\n\n")

#     return response

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="demo.idp", port=443, ssl_context=("certificates/server.crt", "certificates/server.key"), debug=True)