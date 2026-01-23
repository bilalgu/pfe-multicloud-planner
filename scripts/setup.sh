#!/bin/bash

# Script de setup automatique pour le projet

set -e

echo "=== Setup du projet ==="

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "Erreur: Python 3 n'est pas installé"
    exit 1
fi

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo "Erreur: Node.js n'est pas installé"
    exit 1
fi

echo "Python: $(python3 --version)"
echo "Node.js: $(node --version)"

# Setup backend
echo ""
echo "=== Setup Backend ==="
cd backend

if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel Python..."
    python3 -m venv venv
fi

echo "Activation de l'environnement virtuel..."
source venv/bin/activate

echo "Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer .env si n'existe pas
if [ ! -f ".env" ]; then
    echo "Création de .env depuis .env.example..."
    cp .env.example .env
    echo "Fichier .env créé. Éditez-le pour ajouter votre GEMINI_API_KEY"
fi

cd ..

# Setup frontend
echo ""
echo "=== Setup Frontend ==="
cd frontend

echo "Installation des dépendances Node.js..."
npm install

cd ..

echo ""
echo "=== Setup terminé ==="
echo ""
echo "Pour lancer le backend:"
echo "  cd backend && source venv/bin/activate && python app.py"
echo ""
echo "Pour lancer le frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Ou utilisez: make dev"
