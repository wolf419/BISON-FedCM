from flask import Flask, render_template, request
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))
from bison import unblind, blind, verify_signature, serialize_point_uncompressed, unserialize_point_uncompressed
import base64
import hashlib
import subprocess

app = Flask(__name__)
audience = "https://demo.rp"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():

    r = int.from_bytes(base64.b64decode(request.form.get("r")))
    sig = base64.b64decode(request.form.get("sig"))
    A_serialized = request.form.get("A")
    B_serialized = request.form.get("B")
    A = unserialize_point_uncompressed(A_serialized)
    B = unserialize_point_uncompressed(B_serialized)

    result = subprocess.run(["./hash-to-curve/htc", audience], capture_output=True, text=True)
    AudienceId = unserialize_point_uncompressed(result.stdout.strip())
    A_check = blind(AudienceId, r)

    is_valid_A = A == A_check
    is_valid_sig = verify_signature(sig, A_serialized+B_serialized)

    pseudonym_point = unblind(B, r)

    if not is_valid_A or not is_valid_sig:
        token = "not valid"
    else:
        token = hashlib.sha384(serialize_point_uncompressed(pseudonym_point).encode()).digest().hex()

    return render_template("login.html", token=token)

if __name__ == "__main__":
    app.run(host="demo.rp", port=8000, ssl_context=("certificates/server.crt", "certificates/server.key"), debug=True)