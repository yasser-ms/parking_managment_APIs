from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt, exceptions
)
import bcrypt
import random

from app.extensions import db
from app.models import Parking

parkings = Blueprint('parkings', __name__)

@parkings.route('/', methods=['GET'])
@jwt_required()
def get_parkings():
    """get all parkings"""

    parkings = Parking.query.all()

    return jsonify({
        'parkings': [
            {
                'id_parking': p.id_parking.strip(),
                'nom': p.nom,
                'adresse': p.adresse,
                'nbrplace': p.nbrplace,
                'places_disponibles': len([pl for pl in p.place if pl.est_dispo])
            } for p in parkings
        ],
        'total': len(parkings)
    }), 200
