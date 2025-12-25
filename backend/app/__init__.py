from flask import Flask
from .config import Config
from .extensions import db, jwt
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    from app.routes.routes import main
    from app.routes.auth import auth
    from app.routes.vehicule import vehicules
    from app.routes.parking import parkings
    from app.routes.places import places
    from app.routes.contrats import contrats
    from app.routes.historique import verifie
    from app.routes.paiement import paiement

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(vehicules, url_prefix='/vehicules')
    app.register_blueprint(parkings, url_prefix='/parkings')
    app.register_blueprint(places, url_prefix='/places')
    app.register_blueprint(contrats, url_prefix='/contrats')
    app.register_blueprint(verifie, url_prefix='/verifie')
    app.register_blueprint(paiement, url_prefix='/paiement')

    with app.app_context():
        db.session.execute(text("SELECT 1"))
        print("DB connection OK")

    return app
