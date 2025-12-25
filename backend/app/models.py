from typing import Optional
import datetime
import decimal
from .extensions import db
from sqlalchemy import ARRAY, Boolean, CHAR, CheckConstraint, Date, DateTime, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship



class Client(db.Model):
    __tablename__ = 'client'
    __table_args__ = (
        CheckConstraint("adresse_mail::text ~* '^[A-Za-z0-9._%%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'::text", name='adresse_mail_check'),
        CheckConstraint('date_de_naissance < CURRENT_DATE', name='client_date_de_naissance_check'),
        CheckConstraint("id_client ~ '^CL[0-9]{5}$'::text", name='client_id_client_check'),
        CheckConstraint("num_telephone::text ~ '^\\+?[0-9]{8,15}$'::text", name='numero_telephone_check'),
        PrimaryKeyConstraint('id_client', name='client_pkey')
    )

    id_client: Mapped[str] = mapped_column(CHAR(7), primary_key=True)
    nom: Mapped[str] = mapped_column(String(50), nullable=False)
    prenom: Mapped[str] = mapped_column(String(50), nullable=False)
    date_de_naissance: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    adresse_mail: Mapped[str] = mapped_column(String(80), nullable=False)
    num_telephone: Mapped[str] = mapped_column(String(15), nullable=False)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    detail_carte: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String(length=26)))

    vehicule: Mapped[list['Vehicule']] = relationship('Vehicule', back_populates='client')
    paiement: Mapped[list['Paiement']] = relationship('Paiement', back_populates='client')


class Parking(db.Model):
    __tablename__ = 'parking'
    __table_args__ = (
        PrimaryKeyConstraint('id_parking', name='parking_pkey'),
        UniqueConstraint('nom', name='parking_nom_key')
    )

    id_parking: Mapped[str] = mapped_column(CHAR(6), primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    adresse: Mapped[str] = mapped_column(String(100), nullable=False)
    nbrplace: Mapped[int] = mapped_column(Integer, nullable=False)

    borne: Mapped[list['Borne']] = relationship('Borne', back_populates='parking')
    place: Mapped[list['Place']] = relationship('Place', back_populates='parking')


class Borne(db.Model):
    __tablename__ = 'borne'
    __table_args__ = (
        CheckConstraint("etat::text = ANY (ARRAY['en maintenance'::character varying, 'en panne'::character varying, 'active'::character varying]::text[])", name='borne_etat_check'),
        CheckConstraint("id_borne ~ '^B[0-9]{4}$'::text", name='borne_id_borne_check'),
        CheckConstraint("type_de_borne::text = ANY (ARRAY['entree'::character varying, 'sortie'::character varying]::text[])", name='borne_type_de_borne_check'),
        ForeignKeyConstraint(['id_parking'], ['parking.id_parking'], ondelete='CASCADE', onupdate='CASCADE', name='borne_id_parking_fkey'),
        PrimaryKeyConstraint('id_borne', name='borne_pkey')
    )

    id_borne: Mapped[str] = mapped_column(CHAR(5), primary_key=True)
    id_parking: Mapped[str] = mapped_column(CHAR(6), nullable=False)
    type_de_borne: Mapped[str] = mapped_column(String(50), nullable=False)
    etat: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'active'::character varying"))

    parking: Mapped['Parking'] = relationship('Parking', back_populates='borne')
    verifie: Mapped[list['Verifie']] = relationship('Verifie', back_populates='borne')


class Place(db.Model):
    __tablename__ = 'place'
    __table_args__ = (
        CheckConstraint("type_place::text = ANY (ARRAY['voiture'::character varying, 'moto'::character varying, 'bus'::character varying, 'camion'::character varying]::text[])", name='place_type_place_check'),
        ForeignKeyConstraint(['id_parking'], ['parking.id_parking'], ondelete='CASCADE', onupdate='CASCADE', name='place_id_parking_fkey'),
        PrimaryKeyConstraint('id_place', name='place_pkey')
    )

    id_place: Mapped[str] = mapped_column(CHAR(4), primary_key=True)
    id_parking: Mapped[str] = mapped_column(CHAR(6), nullable=False)
    est_dispo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    type_place: Mapped[Optional[str]] = mapped_column(String(20))

    parking: Mapped['Parking'] = relationship('Parking', back_populates='place')
    contrat: Mapped[list['Contrat']] = relationship('Contrat', back_populates='place')


class Vehicule(db.Model):
    __tablename__ = 'vehicule'
    __table_args__ = (
        CheckConstraint("id_vehicule ~ '^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$'::text", name='vehicule_id_vehicule_check'),
        CheckConstraint("type::text = ANY (ARRAY['voiture'::character varying, 'moto'::character varying, 'camion'::character varying, 'bus'::character varying, 'utilitaire'::character varying]::text[])", name='vehicule_type_check'),
        ForeignKeyConstraint(['id_client'], ['client.id_client'], ondelete='CASCADE', onupdate='CASCADE', name='vehicule_id_client_fkey'),
        PrimaryKeyConstraint('id_vehicule', name='vehicule_pkey')
    )

    id_vehicule: Mapped[str] = mapped_column(CHAR(9), primary_key=True)
    id_client: Mapped[str] = mapped_column(CHAR(7), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'voiture'::character varying"))
    modele: Mapped[Optional[str]] = mapped_column(String(50))

    client: Mapped['Client'] = relationship('Client', back_populates='vehicule')
    contrat: Mapped[list['Contrat']] = relationship('Contrat', back_populates='vehicule')


class Contrat(db.Model):
    __tablename__ = 'contrat'
    __table_args__ = (
        CheckConstraint('date_fin >= date_debut', name='contrat_check'),
        CheckConstraint("etat_contrat::text = ANY (ARRAY['actif'::character varying, 'expiré'::character varying, 'résilié'::character varying]::text[])", name='contrat_etat_contrat_check'),
        CheckConstraint("id_contrat ~ '^CT[0-9]{5}$'::text", name='contrat_id_contrat_check'),
        CheckConstraint("id_place ~ '^P[0-9]{3}$'::text", name='check_id_place'),
        CheckConstraint("type_contrat::text = ANY (ARRAY['abonnement'::character varying, 'ticketHoraire'::character varying]::text[])", name='contrat_type_contrat_check'),
        ForeignKeyConstraint(['id_place'], ['place.id_place'], ondelete='CASCADE', name='contrat_id_place_fkey'),
        ForeignKeyConstraint(['id_vehicule'], ['vehicule.id_vehicule'], ondelete='CASCADE', name='contrat_id_vehicule_fkey'),
        PrimaryKeyConstraint('id_contrat', name='contrat_pkey')
    )

    id_contrat: Mapped[str] = mapped_column(CHAR(7), primary_key=True)
    id_vehicule: Mapped[str] = mapped_column(CHAR(9), nullable=False)
    id_place: Mapped[str] = mapped_column(CHAR(4), nullable=False)
    date_debut: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    date_fin: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    etat_contrat: Mapped[str] = mapped_column(String(10), nullable=False)
    type_contrat: Mapped[str] = mapped_column(String(20), nullable=False)

    place: Mapped['Place'] = relationship('Place', back_populates='contrat')
    vehicule: Mapped['Vehicule'] = relationship('Vehicule', back_populates='contrat')
    paiement: Mapped['Paiement'] = relationship('Paiement', uselist=False, back_populates='contrat')
    penalite: Mapped[list['Penalite']] = relationship('Penalite', back_populates='contrat')
    verifie: Mapped[list['Verifie']] = relationship('Verifie', back_populates='contrat')


class Abonnement(Contrat):
    __tablename__ = 'abonnement'
    __table_args__ = (
        CheckConstraint('tarif_mensuel > 0::numeric', name='abonnement_tarif_mensuel_check'),
        ForeignKeyConstraint(['id_abonnement'], ['contrat.id_contrat'], ondelete='CASCADE', onupdate='CASCADE', name='abonnement_id_abonnement_fkey'),
        PrimaryKeyConstraint('id_abonnement', name='abonnement_pkey')
    )

    id_abonnement: Mapped[str] = mapped_column(CHAR(7), primary_key=True)
    tarif_mensuel: Mapped[decimal.Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    renouvelable: Mapped[Optional[bool]] = mapped_column(Boolean)


class Paiement(db.Model):
    __tablename__ = 'paiement'
    __table_args__ = (
        CheckConstraint("id_paiement ~ '^PMT[0-9]{4}$'::text", name='paiement_id_paiement_check'),
        CheckConstraint('montant > 0::numeric', name='paiement_montant_check'),
        ForeignKeyConstraint(['id_client'], ['client.id_client'], ondelete='CASCADE', onupdate='CASCADE', name='paiement_id_client_fkey'),
        ForeignKeyConstraint(['id_contrat'], ['contrat.id_contrat'], ondelete='CASCADE', onupdate='CASCADE', name='paiement_id_contrat_fkey'),
        PrimaryKeyConstraint('id_paiement', name='paiement_pkey'),
        UniqueConstraint('id_contrat', name='paiement_id_contrat_key')
    )

    id_paiement: Mapped[str] = mapped_column(CHAR(7), primary_key=True)
    id_contrat: Mapped[str] = mapped_column(CHAR(7), nullable=False)
    id_client: Mapped[str] = mapped_column(CHAR(7), nullable=False)
    date_paiement: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    montant: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))

    client: Mapped['Client'] = relationship('Client', back_populates='paiement')
    contrat: Mapped['Contrat'] = relationship('Contrat', back_populates='paiement')


class Penalite(db.Model):
    __tablename__ = 'penalite'
    __table_args__ = (
        CheckConstraint("id_penalite ~ '^PNL[0-9]{4}$'::text", name='penalite_id_penalite_check'),
        CheckConstraint('montant_p > 0::numeric', name='penalite_montant_p_check'),
        ForeignKeyConstraint(['id_contrat'], ['contrat.id_contrat'], ondelete='CASCADE', onupdate='CASCADE', name='penalite_id_contrat_fkey'),
        PrimaryKeyConstraint('id_penalite', name='penalite_pkey')
    )

    id_penalite: Mapped[str] = mapped_column(CHAR(7), primary_key=True)
    id_contrat: Mapped[str] = mapped_column(CHAR(7), nullable=False)
    montant_p: Mapped[decimal.Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text('NULL::character varying'))
    date_creation: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    contrat: Mapped['Contrat'] = relationship('Contrat', back_populates='penalite')


class Tickethoraire(Contrat):
    __tablename__ = 'tickethoraire'
    __table_args__ = (
        CheckConstraint('tarif_horaire > 0::numeric', name='tickethoraire_tarif_horaire_check'),
        ForeignKeyConstraint(['id_ticket'], ['contrat.id_contrat'], ondelete='CASCADE', onupdate='CASCADE', name='tickethoraire_id_ticket_fkey'),
        PrimaryKeyConstraint('id_ticket', name='tickethoraire_pkey')
    )

    id_ticket: Mapped[str] = mapped_column(CHAR(7), primary_key=True)
    duree_totale: Mapped[datetime.timedelta] = mapped_column(INTERVAL, nullable=False)
    tarif_horaire: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2))


class Verifie(db.Model):
    __tablename__ = 'verifie'
    __table_args__ = (
        CheckConstraint("etat_valide::text = ANY (ARRAY['encours_in'::character varying, 'encours_out'::character varying, 'delai_depasse'::character varying]::text[])", name='verifie_etat_valide'),
        ForeignKeyConstraint(['id_borne'], ['borne.id_borne'], ondelete='CASCADE', onupdate='CASCADE', name='verifie_id_borne_fkey'),
        ForeignKeyConstraint(['id_contrat'], ['contrat.id_contrat'], ondelete='CASCADE', onupdate='CASCADE', name='verifie_id_contrat_fkey'),
        PrimaryKeyConstraint('id_contrat', 'id_borne', name='verifie_pkey')
    )

    id_contrat: Mapped[str] = mapped_column(CHAR(7), primary_key=True)
    id_borne: Mapped[str] = mapped_column(CHAR(5), primary_key=True)
    heure_scanne: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    etat_valide: Mapped[str] = mapped_column(String(50), nullable=False)

    borne: Mapped['Borne'] = relationship('Borne', back_populates='verifie')
    contrat: Mapped['Contrat'] = relationship('Contrat', back_populates='verifie')
