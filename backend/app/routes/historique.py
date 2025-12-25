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

from datetime import datetime

from app.extensions import db
from app.models import Verifie

verifie = Blueprint('verifie', __name__)


@verifie.route('/', methods=['GET'])
@jwt_required()
def get_historique():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data received'}), 400

        
        if 'id_contrat' not in data or 'id_borne' not in data:
            return jsonify({'error': 'id_contrat et id_borne requis'}), 400

       
        historique = db.session.query(Verifie).filter_by(
            id_contrat=data['id_contrat'],
            id_borne=data['id_borne']
        ).first()

        if not historique:
            return jsonify({'error': 'Historique non trouvé'}), 404

        return jsonify({
            'historique': {
                'id_contrat': historique.id_contrat.strip(),
                'id_borne': historique.id_borne.strip(),
                'heure_scanne': historique.heure_scanne.isoformat(),
                'etat_valide': historique.etat_valide
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@verifie.route('/contrat/<string:id_contrat>', methods=['GET'])
@jwt_required()
def get_historique_by_contrat(id_contrat):
    """Get all historique for a contrat"""
    try:
        historique = db.session.query(Verifie).filter_by(id_contrat=id_contrat).all()

        return jsonify({
            'historique': [
                {
                    'id_contrat': h.id_contrat.strip(),
                    'id_borne': h.id_borne.strip(),
                    'heure_scanne': h.heure_scanne.isoformat(),
                    'etat_valide': h.etat_valide
                } for h in historique
            ],
            'total': len(historique)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
