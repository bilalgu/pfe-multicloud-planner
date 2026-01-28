# Backend - API Flask

## Architecture

```
Phrase utilisateur
    ↓
app.py (Flask POST /generate)
    ↓
modules/nlp.py (Gemini NLP)
    ↓
modules/terraform_gen.py (Generation TF)
    ↓
modules/security.py (Validation)
    ↓
JSON response (OK/NOT_OK + Terraform)
```

## Structure

```
backend/
├── modules/
│   ├── nlp.py
│   ├── terraform_gen.py
│   ├── security_rules.py
│   └── security.py
├── tests/
│   ├── test_api.py
│   ├── test_nlp.py
│   ├── test_security.py
│   └── test_terraform_gen.py
├── app.py
└── requirements.txt
```

---

## Setup

### Option 1 : Make (recommandé)

```bash
make setup  # Installe tout + crée .env
make dev    # Lance backend + frontend
```

### Option 2 : Manuel

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Éditer .env : ajouter GEMINI_API_KEY ou mettre AI_MODE=mock
python app.py
```

Voir `QUICKSTART.md` et `CONTRIBUTING.md` pour plus de détails.

---

## Endpoints

### POST /generate

Genere une infrastructure Terraform securisee.

1. **Request** :

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux un serveur AWS"}'
```

**Response OK** :

```json
{
  "json": {
    "databases": 0,
    "load_balancers": 0,
    "networks": 1,
    "provider": "aws",
    "security_groups": 1,
    "servers": 1
  },
  "security": "OK",
  "security_report": {
    "grade": "C",
    "score": 70,
    "status": "OK"
  },
  "terraform": "# Infrastructure as Code..."
}
```

2. **Request** :

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux une base de donnees MySQL publique"}'
```

**Response NOT_OK** (demande dangereuse) :

```json
{
  "json": {...},
  "security": "NOT_OK",
  "security_report": {
    "dangerous_requests": [
      {
        "applied": "Base de donnees PRIVEE (politique de securite)",
        "reason": "Les bases de donnees ne doivent jamais etre accessibles depuis Internet",
        "requested": "Base de donnees publique"
      }
    ],
    "status": "NOT_OK"
  },
  "terraform": "BLOCKED"
}
```

3. **Request** :

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux un serveur Azure"}'
```

**Response NOT_OK** (score bas) :

```json
{
  "json": {...},
  "security": "NOT_OK",
  "security_report": {
    "status": "NOT_OK",
    "violations": [
      {
        "category": "Encryption",
        "description": "Les donnees doivent etre chiffrees au repos",
        "rule": "encryption_at_rest",
        "severity": "HIGH"
      },
      {
        "category": "Encryption",
        "description": "Les connexions doivent utiliser SSL/TLS",
        "rule": "ssl_required",
        "severity": "HIGH"
      },
      {
        "category": "Monitoring",
        "description": "La surveillance et les logs doivent etre actives",
        "rule": "monitoring_enabled",
        "severity": "MEDIUM"
      },
      {
        "category": "Backup & Recovery",
        "description": "Les sauvegardes doivent etre configurees",
        "rule": "backup_enabled",
        "severity": "MEDIUM"
      }
    ]
  },
  "terraform": "BLOCKED"
}
```

### GET /health

Verifie que le backend est operationnel.

```bash
curl http://localhost:5000/health
```

**Response** :

```json
{
  "status": "ok"
}
```

### GET /api/history

Journal des runs

```bash
curl http://localhost:5000/api/history
```

**Response** :

```json
{
  "runs": [
    {
      "timestamp": "2026-01-27T10:20:34.108474",
      "phrase": "Je veux 3 serveurs web AWS avec un load balancer",
      "infra": {
        "provider": "aws",
        "servers": 3,
        "load_balancers": 1,
        "databases": 0,
        "networks": 1,
        "security_groups": 1
      },
      "security_status": "OK",
      "terraform_status": "GENERATED",
      "security_score": 90
    }
  ],
  "total": 1
}
```

---

## Politiques de securite

### Detection proactive (dans la phrase)

1. **Base de donnees publique** → Bloque
2. **Sans chiffrement** → Bloque
3. **SSH ouvert au public** → Bloque

### Verification code genere (6 regles MVP)

1. `db_no_public_ip` - Base privee obligatoire (HIGH)
2. `encryption_at_rest` - Chiffrement au repos (HIGH)
3. `ssl_required` - SSL/TLS obligatoire (HIGH)
4. `monitoring_enabled` - Surveillance active (MEDIUM)
5. `backup_enabled` - Sauvegardes configurees (MEDIUM)
6. `no_hardcoded_credentials` - Pas de passwords en dur (CRITICAL)

**Seuil de blocage** : Score < 70

Voir `BACKLOG.md` pour roadmap complète.