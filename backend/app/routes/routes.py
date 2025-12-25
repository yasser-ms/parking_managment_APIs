from flask import Blueprint, jsonify
from app.models import Client
from app.extensions import db

main = Blueprint("main", __name__)

## This file is only used for testing, there is no important endpoints here

@main.route("/")
def home():
    return {"status": "Flask is running"}


@main.route("/clients")
def clients():
    try:
        clients = Client.query.limit(10).all()
        return jsonify([
            {"id_client": c.id_client.strip(), "nom": c.nom, "prenom": c.prenom, "email": c.adresse_mail}
            for c in clients
        ])
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500
