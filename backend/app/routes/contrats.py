from flask import Blueprint, request, jsonify
from sqlalchemy import text
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
from app.models import Contrat, Client, Vehicule, Abonnement, Tickethoraire, Place, Parking

from datetime import datetime, timedelta
import random

contrats = Blueprint('contrats', __name__)

## get all contrats of the client
@contrats.route('/', methods=['GET'])
@jwt_required()
def get_contrats():
    try:
        id_client = get_jwt_identity()
        my_vehicules = db.session.query(Vehicule).filter_by(id_client=id_client).all()
        vehicule_id = my_vehicules[0].id_vehicule
        contrats = Contrat.query.filter(Contrat.id_vehicule == vehicule_id).all()

        return jsonify({
            'success': 'yes',
            'contrats': [
                {
                    'id_contrat': c.id_contrat.strip(),
                    'id_vehicule': c.id_vehicule.strip(),
                    'id_place': c.id_place.strip(),
                    'date_debut': c.date_debut,
                    'date_fin': c.date_fin,
                    'etat_contrat': c.etat_contrat.strip(),
                    'type_contrat': c.type_contrat.strip(),
                } for c in contrats
            ],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


## Buy a contrat based on the type-contrat, date_debut, la durée, -> generate id_contart
## and then payments using another endPoint



def generate_contrat_id():
    """Generate unique contrat ID: CT00000"""
    while True:
        new_id = f"CT{random.randint(10000, 99999)}"
        existing = db.session.get(Contrat, new_id)
        if not existing:
            return new_id


@contrats.route('/', methods=['POST'])
@jwt_required()
def create_contrat():
    """Create a new contrat (abonnement or ticketHoraire)"""
    try:
        client_id = get_jwt_identity()
        data = request.get_json()
        id_parking = Parking.query.filter(Parking.id_parking == data['id_parking']).first()

    
        required = ['type_contrat', 'id_vehicule', 'id_place', 'date_debut', 'duree','id_parking']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400

        valid_types = ['abonnement', 'ticketHoraire']
        c_type = data.get('type_contrat')
        if c_type not in valid_types:
            return jsonify({'error': f'Type invalide. Choisissez parmi: {valid_types}'}), 400

        vehicule = db.session.get(Vehicule, data['id_vehicule'])
        if not vehicule:
            return jsonify({'error': 'Véhicule non trouvé'}), 404
        if vehicule.id_client.strip() != client_id.strip():
            return jsonify({'error': 'Ce véhicule ne vous appartient pas'}), 403


        place = db.session.get(Place, data['id_place'])
        if not place:
            return jsonify({'error': 'Place non trouvée'}), 404
        if not place.est_dispo:
            return jsonify({'error': 'Cette place n\'est pas disponible'}), 400
        if place.id_parking.strip() != data['id_parking'].strip():
            return jsonify({'error': 'Cette place n\'est pas dans ce parking'}), 400

  
        date_debut = datetime.fromisoformat(data['date_debut'])
        duree = data['duree']  # in hours for ticket, in days for abonnement

        if c_type == 'ticketHoraire':
            date_fin = date_debut + timedelta(hours=duree)
        else:  
            date_fin = date_debut + timedelta(days=duree)

     
        contrat_id = generate_contrat_id()


        new_contrat = Contrat(
            id_contrat=contrat_id,
            id_vehicule=data['id_vehicule'],
            id_place=data['id_place'],
            date_debut=date_debut,
            date_fin=date_fin,
            etat_contrat='actif',
            type_contrat=c_type
        )
        db.session.add(new_contrat)

        
        place.est_dispo = False

        db.session.commit()

   
        if c_type == 'abonnement':
            tarif_mensuel = data.get('tarif_mensuel', 50.00)
            renouvelable = data.get('renouvelable', True)
            db.session.execute(
                text("""
                    INSERT INTO abonnement (id_abonnement, tarif_mensuel, renouvelable)
                    VALUES (:id, :tarif, :renouv)
                """),
                {'id': contrat_id, 'tarif': tarif_mensuel, 'renouv': renouvelable}
            )
        else: 
            tarif_horaire = data.get('tarif_horaire', 2.50)
            db.session.execute(
                text("""
                    INSERT INTO tickethoraire (id_ticket, tarif_horaire, duree_totale)
                    VALUES (:id, :tarif, :duree)
                """),
                {'id': contrat_id, 'tarif': tarif_horaire, 'duree': timedelta(hours=duree)}
            )

        return jsonify({
            'message': 'Contrat créé avec succès',
            'contrat': {
                'id_contrat': contrat_id,
                'type_contrat': c_type,
                'id_vehicule': data['id_vehicule'],
                'id_place': data['id_place'],
                'date_debut': date_debut.isoformat(),
                'date_fin': date_fin.isoformat(),
                'etat_contrat': 'actif',
                'paiement': 'en attente'
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


## reslier contrat -> Delete from DB
@contrats.route('/<string:id_contart>', methods=['DELETE'])
@jwt_required()
def delete_contrat(id_contart):
    try:
        contrat = db.session.query(Contrat).filter(Contrat.id_contrat == id_contart).first()
        id_place = contrat.id_place

        #make the place disponible
        place = db.session.query(Place).filter(Place.id_place == id_place).first()
        place.est_dispo = True

        abnm = db.session.query(Abonnement).filter(Abonnement.id_abonnement == id_contart).first()
        tktH = db.session.query(Tickethoraire).filter(Tickethoraire.id_ticket == id_contart).first()

        if tktH:
            db.session.delete(tktH)
        if abnm:
            db.session.delete(abnm)

        db.session.delete(contrat)
        db.session.commit()
        return jsonify({'success': 'contart supprimer'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

