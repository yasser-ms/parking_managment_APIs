from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
import bcrypt
import random

from app.extensions import db
from app.models import Client

auth = Blueprint('auth', __name__)


blacklist = set()


def generate_client_id():
    """Generate unique client ID: CL00000"""
    while True:
        new_id = f"CL{random.randint(10000, 99999)}"
        existing = db.session.get(Client, new_id)
        if not existing:
            return new_id


@auth.route('/register', methods=['POST'])
def register():
    """Register a new client"""
    try:
        data = request.get_json()

      
        required = ['nom', 'prenom', 'date_de_naissance', 'adresse_mail', 'num_telephone', 'password']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400

        existing = db.session.query(Client).filter_by(adresse_mail=data['adresse_mail']).first()
        if existing:
            return jsonify({'error': 'Cette adresse email est déjà utilisée'}), 409
            
        hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


        new_client = Client(
            id_client=generate_client_id(),
            nom=data['nom'],
            prenom=data['prenom'],
            date_de_naissance=data['date_de_naissance'],
            adresse_mail=data['adresse_mail'],
            num_telephone=data['num_telephone'],
            password=hashed,
            detail_carte=data.get('detail_carte')
        )

        db.session.add(new_client)
        db.session.commit()


        access_token = create_access_token(identity=new_client.id_client)
        refresh_token = create_refresh_token(identity=new_client.id_client)

        return jsonify({
            'message': 'Inscription réussie',
            'client': {
                'id_client': new_client.id_client.strip(),
                'nom': new_client.nom,
                'prenom': new_client.prenom,
                'adresse_mail': new_client.adresse_mail
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth.route('/login', methods=['POST'])
def login():
    """Login client"""
    try:
        data = request.get_json()

        if not data.get('adresse_mail') or not data.get('password'):
            return jsonify({'error': 'Email et mot de passe requis'}), 400


        client = db.session.query(Client).filter_by(adresse_mail=data['adresse_mail']).first()

        if not client:
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

       
        if not bcrypt.checkpw(data['password'].encode('utf-8'), client.password.encode('utf-8')):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401


        access_token = create_access_token(identity=client.id_client)
        refresh_token = create_refresh_token(identity=client.id_client)

        return jsonify({
            'message': 'Connexion réussie',
            'client': {
                'id_client': client.id_client.strip(),
                'nom': client.nom,
                'prenom': client.prenom,
                'adresse_mail': client.adresse_mail
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout - invalidate token"""
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'message': 'Déconnexion réussie'}), 200


@auth.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """Get current user profile"""
    try:
        client_id = get_jwt_identity()
        client = db.session.get(Client, client_id)

        if not client:
            return jsonify({'error': 'Client non trouvé'}), 404

        return jsonify({
            'id_client': client.id_client.strip(),
            'nom': client.nom,
            'prenom': client.prenom,
            'adresse_mail': client.adresse_mail,
            'num_telephone': client.num_telephone,
            'date_de_naissance': client.date_de_naissance.isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Get new access token"""
    client_id = get_jwt_identity()
    access_token = create_access_token(identity=client_id)
    return jsonify({'access_token': access_token}), 200
