# Démarrage rapide

## Installation en 3 étapes

### 1. Setup automatique

```bash
make setup
```

Cette commande :
- Crée l'environnement virtuel Python
- Installe les dépendances backend
- Installe les dépendances frontend
- Crée le fichier `.env` depuis `.env.example`

### 2. Configurer l'API (optionnel)

Éditez `backend/.env` :
- Ajoutez votre `GEMINI_API_KEY` pour utiliser l'API réelle
- Ou laissez `AI_MODE=mock` pour le mode développement (sans API)

### 3. Lancer le projet

```bash
make dev
```

Cette commande lance :
- Backend sur http://localhost:5000
- Frontend sur http://localhost:3000

## Commandes utiles

```bash
make help          # Voir toutes les commandes
make test          # Lancer les tests
make clean         # Nettoyer les fichiers générés
```

## Alternative : Scripts shell

```bash
# Setup
./scripts/setup.sh

# Lancer
./scripts/dev.sh
```

## Dépannage

### Backend ne démarre pas

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Frontend ne démarre pas

```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Port déjà utilisé

- Backend : Modifier le port dans `backend/app.py` (ligne 70)
- Frontend : Next.js utilise automatiquement le port suivant (3001, 3002...)
