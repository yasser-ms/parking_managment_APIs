# Parking Management API

A RESTful API for managing parking lots, reservations, and payments built with Flask and PostgreSQL.

## Tech Stack

- **Backend:** Flask, SQLAlchemy
- **Database:** PostgreSQL
- **Authentication:** JWT (Flask-JWT-Extended)
- **Containerization:** Docker, Docker Compose
- **Password Hashing:** Bcrypt

## Features

- User authentication (register, login, logout)
- Vehicle management (CRUD)
- Parking lots with real-time availability
- Place management by type (voiture, moto, camion, bus)
- Contract creation (abonnement / ticket horaire)
- Payment processing
- Entry/Exit history tracking (bornes)
- Penalties management

## Quick Start

### With Docker
```bash
docker-compose up -d --build
```

### Without Docker
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
python run.py
```

## API Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/auth/register` | POST | Register new user |  
| `/auth/login` | POST | Login |  
| `/auth/me` | GET | Get current user | 
| `/vehicules/` | GET | Get my vehicles | 
| `/vehicules/` | POST | Add vehicle | 
| `/parkings/` | GET | List all parkings | 
| `/places/` | GET | List all places | 
| `/contrats/` | POST | Create contract | 
| `/paiements/` | POST | Make payment | 
| `/verifie/contrat/<id>` | GET | Get entry/exit history | 


## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   └── routes/
│       ├── auth.py
│       ├── vehicules.py
│       ├── parkings.py
│       ├── places.py
│       ├── contrats.py
│       ├── paiements.py
│       └── verifie.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── run.py
```
## Next -> Front end

## 👤 Author

**Yasser MOUSSAOUI**
