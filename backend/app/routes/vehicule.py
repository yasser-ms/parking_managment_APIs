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
from app.models import Vehicule

vehicules = Blueprint('vehicules', __name__)


@vehicules.route('/', methods=['GET'])
@jwt_required()
def get_vehicule():
    """Get vehicules of the client """
    try:
        client_id = get_jwt_identity()
        my_vehicules = db.session.query(Vehicule).filter_by(id_client=client_id).all()

        return jsonify({
            'vehicules': [
                {
                    'id_vehicule': v.id_vehicule.strip(),
                    'type': v.type,
                    'modele': v.modele
                } for v in my_vehicules
            ],
            'total': len(my_vehicules)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@vehicules.route('/', methods=['POST'])
@jwt_required()
def add_vehicule():
    """Add a new vehicle"""
    try:
        client_id = get_jwt_identity()
        data = request.get_json()

    
        if 'id_vehicule' not in data:
            return jsonify({'error': 'Le champ id_vehicule est requis (format: XX-000-XX)'}), 400

        
        import re
        if not re.match(r'^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$', data['id_vehicule']):
            return jsonify({'error': 'Format invalide. Utilisez: XX-000-XX (ex: AB-123-CD)'}), 400

       
        existing = db.session.get(Vehicule, data['id_vehicule'])
        if existing:
            return jsonify({'error': 'Ce véhicule est déjà enregistré'}), 409

        
        valid_types = ['voiture', 'moto', 'camion', 'bus', 'utilitaire']
        v_type = data.get('type', 'voiture')
        if v_type not in valid_types:
            return jsonify({'error': f'Type invalide. Choisissez parmi: {valid_types}'}), 400

        new_vehicule = Vehicule(
            id_vehicule=data['id_vehicule'],
            id_client=client_id,
            type=v_type,
            modele=data.get('modele')
        )

        db.session.add(new_vehicule)
        db.session.commit()

        return jsonify({
            'message': 'Véhicule ajouté avec succès',
            'vehicule': {
                'id_vehicule': new_vehicule.id_vehicule.strip(),
                'type': new_vehicule.type,
                'modele': new_vehicule.modele
            }
        }),
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@vehicules.route('/<string:id_vehicule>', methods=['DELETE'])
@jwt_required()
def delete_vehicule(id_vehicule):
    try:
        id_client = get_jwt_identity()
        vehicule = db.session.query(Vehicule).filter_by(id_vehicule=id_vehicule).first()
        
        db.session.delete(vehicule)
        db.session.commit()

        return jsonify({
            'message': 'suppression de vehicule avec succés',
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

