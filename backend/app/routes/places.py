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
from app.models import Parking, Place

places = Blueprint('places', __name__)


@places.route('/', methods=['GET'])
@jwt_required()
def get_places():
    """Get all places with stats by type and parking"""
    try:
        places_list = db.session.query(Place).all()
        parkings = db.session.query(Parking).all()

 
        types = ['voiture', 'moto', 'camion', 'bus']

        
        disponibles_par_type = {}
        for t in types:
            disponibles_par_type[t] = db.session.query(Place).filter_by(est_dispo=True, type_place=t).count()

     
        disponibles_par_parking = {}
        for parking in parkings:
            par_type = {}
            for t in types:
                par_type[t] = db.session.query(Place).filter_by(
                    est_dispo=True,
                    id_parking=parking.id_parking,
                    type_place=t
                ).count()

            disponibles_par_parking[parking.id_parking.strip()] = {
                'nom': parking.nom,
                'total_disponibles': db.session.query(Place).filter_by(est_dispo=True,
                                                                       id_parking=parking.id_parking).count(),
                'par_type': par_type
            }

        return jsonify({
            'places': [
                {
                    'id_place': p.id_place.strip(),
                    'id_parking': p.id_parking.strip(),
                    'type_place': p.type_place,
                    'est_dispo': p.est_dispo
                } for p in places_list
            ],
            'total': len(places_list),
            'disponibles_par_type': disponibles_par_type,
            'disponibles_par_parking': disponibles_par_parking
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
