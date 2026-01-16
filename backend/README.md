 Backend - Infrastructure Generator

Backend Flask avec Gemini AI pour la génération d'infrastructure multi-cloud.

# 📁 Structure

backend/
├── app.py                    # Application Flask principale 
├── security_rules.py         # Bibliothèque de politiques
├── requirements.txt          # Dépendances
└── .env             # Template configuration


#  Architecture du code

app.py - Organisation en sections

# ÉTAPE 1 : EXPRESSION DES BESOINS
- Configuration Gemini AI
- Schéma JSON structuré
- Extraction NLP

# ÉTAPE 2 : INTERFACE MULTI-CLOUD
- Configuration AWS, Azure, GCP, OpenStack
- Templates optimisés

# ÉTAPE 3 : MOTEURS IA/IAC
- generate_terraform_code()
- generate_ansible_playbook()

# ÉTAPE 4 : ROUTES API
- POST /generate
- GET /health


#security_rules.py - Module de sécurité

SECURITY_POLICIES = {
    "db_no_public_ip": {...},
    "encryption_at_rest": {...},
    "ssl_required": {...},
    "monitoring_enabled": {...},
    "backup_enabled": {...},
    "no_hardcoded_credentials": {...}
}

# Fonctions principales
- get_secure_settings() : Paramètres sécurisés pour génération
- check_terraform_security() : Validation post-génération


##  Installation

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Ajouter GEMINI_API_KEY dans .env
```

 Lancement

python app.py
# → http://localhost:5000
```

  API

POST /generate

**Request:**
```json
{
  "description": "Je veux 3 serveurs AWS avec MySQL"
}
```

**Response:**
```json
{
  "success": true,
  "infrastructure": {...},
  "terraform_code": "...",
  "ansible_playbook": "...",
  "security_report": {
    "security_score": 100,
    "security_grade": "A"
  }
}
```

 GET /health

Response:
```json
{
  "status": "ok",
  "supported_providers": ["aws", "azure", "gcp", "openstack"]
}
```

##  Tests

# Test de santé
curl http://localhost:5000/health

# Test de génération
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Un serveur AWS"}'


#  Sécurité

- Clé API Gemini dans `.env` (jamais commité)
- Variables sensibles marquées `sensitive = true`
- Validation des entrées utilisateur
- Règles de sécurité appliquées automatiquement

#  Dépendances

- Flask 3.0+ : Framework web
- flask-cors 4.0+ : Support CORS
- python-dotenv 1.0+ : Variables d'environnement
- google-genai 0.3+ : API Gemini AI
