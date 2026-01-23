# Guide de contribution

## Développement local

### Prérequis
- Python 3.11+
- Node.js 20+
- Make (optionnel, pour utiliser les commandes make)

### Setup rapide (avec Make)

```bash
# Setup complet
make setup

# Lancer backend et frontend
make dev

# Tests
make test
```

### Setup manuel

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt

# Créer .env depuis .env.example
cp .env.example .env
# Éditer .env et ajouter votre GEMINI_API_KEY ou mettre AI_MODE=mock

# Lancer
python app.py
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
# Avec Make
make test

# Manuellement
# Backend
cd backend
source venv/bin/activate
export AI_MODE=mock
pytest tests/ -v

# Frontend
cd frontend
npm run lint
```

### Scripts shell

```bash
# Setup automatique
./scripts/setup.sh

# Lancer backend + frontend
./scripts/dev.sh
```

## Standards de code

### Python
- Utiliser type hints
- Docstrings Google style
- Format: black (recommandé)
- Linter: pylint ou flake8

### TypeScript/React
- TypeScript strict mode
- Composants fonctionnels avec hooks
- ESLint configuré

## Processus de PR

1. Créer une branche depuis `main`
2. Faire vos modifications
3. Ajouter des tests si nécessaire
4. Vérifier que les tests passent
5. Créer une PR avec description claire

## Structure du projet

```
pfe-multicloud-planner/
├── backend/          # API Flask
│   ├── modules/     # Modules métier
│   ├── tests/       # Tests unitaires
│   └── app.py       # Point d'entrée
├── frontend/        # Next.js
│   └── app/         # Pages et composants
└── docs/            # Documentation

```
