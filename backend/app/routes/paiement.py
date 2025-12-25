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
from app.models import Paiement, Contrat, Abonnement, Tickethoraire

paiement = Blueprint('paiement', __name__)

@paiement.route('/', methods=['GET'])
@jwt_required()
def get_paiement():
    id_client = get_jwt_identity()
    paiements = db.session.query(Paiement).filter(Paiement.id_client == id_client).all()

    return jsonify(
        {
           'id_paiement' : paiement.id_paiement,
            'id_contart' : paiement.id_contart,
            'id_client' : paiement.id_client,
            'date_paiement' : paiement.date_paiement,
            'montant' : paiement.montant,
        } for paiement in paiements
    )


@paiement.route('/', methods=['POST'])
@jwt_required()
def create_paiement():
    """Pay for a contrat"""
    try:
        client_id = get_jwt_identity()
        data = request.get_json()

        if 'id_contrat' not in data:
            return jsonify({'error': 'id_contrat requis'}), 400


        contrat = db.session.get(Contrat, data['id_contrat'])
        if not contrat:
            return jsonify({'error': 'Contrat non trouvé'}), 404

        existing_paiement = db.session.query(Paiement).filter_by(id_contrat=data['id_contrat']).first()
        if existing_paiement:
            return jsonify({'error': 'Ce contrat est déjà payé'}), 409

     
        if contrat.type_contrat == 'abonnement':
            abonnement = db.session.get(Abonnement, contrat.id_contrat)
            montant = float(abonnement.tarif_mensuel)
        else:
            ticket = db.session.get(Tickethoraire, contrat.id_contrat)
            hours = ticket.duree_totale.total_seconds() / 3600
            montant = float(ticket.tarif_horaire) * hours

 
        paiement_id = f"PMT{random.randint(1000, 9999)}"

        new_paiement = Paiement(
            id_paiement=paiement_id,
            id_contrat=contrat.id_contrat,
            id_client=client_id,
            montant=montant,
            date_paiement=datetime.now().date()
        )

        db.session.add(new_paiement)
        db.session.commit()

        return jsonify({
            'message': 'Paiement effectué',
            'paiement': {
                'id_paiement': paiement_id,
                'id_contrat': contrat.id_contrat.strip(),
                'montant': montant,
                'date_paiement': new_paiement.date_paiement.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
