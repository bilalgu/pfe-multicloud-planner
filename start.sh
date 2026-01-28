#!/bin/bash

# Script de démarrage rapide pour tester le projet localement

set -e

echo "=== Démarrage du projet ==="
echo ""

# Vérifier les prérequis
if ! command -v python3 &> /dev/null; then
    echo "ERREUR: Python 3 n'est pas installé"
    exit 1
fi

# Charger nvm si disponible
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

if ! command -v node &> /dev/null && ! command -v nodejs &> /dev/null; then
    echo "ATTENTION: Node.js n'est pas installé"
    echo "Pour installer Node.js:"
    echo "  sudo apt install nodejs npm"
    echo ""
    echo "Ou utilisez nvm:"
    echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    echo "  nvm install node"
    echo ""
    echo "Le backend peut fonctionner seul sans Node.js"
    echo ""
    read -p "Continuer avec le backend uniquement ? (o/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[OoYy]$ ]]; then
        exit 1
    fi
    BACKEND_ONLY=true
else
    BACKEND_ONLY=false
fi

# Configuration backend
cd backend
if [ ! -f .env ]; then
    echo "Création du fichier .env pour le backend..."
    echo "AI_MODE=mock" > .env
    echo "Fichier .env créé avec AI_MODE=mock (mode développement)"
    echo "Pour utiliser l'API Gemini réelle, éditez backend/.env et ajoutez:"
    echo "  AI_MODE=real"
    echo "  GEMINI_API_KEY=votre_cle_api"
    echo ""
fi

# Vérifier si venv existe
if [ ! -d "venv" ]; then
    echo "Installation des dépendances backend..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
cd ..

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "Arrêt des processus..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Lancer backend
echo "Démarrage du backend sur http://localhost:5000"
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

sleep 2

# Lancer frontend si Node.js est disponible
if [ "$BACKEND_ONLY" = false ]; then
    # Vérifier si node_modules existe
    if [ ! -d "frontend/node_modules" ]; then
        echo "Installation des dépendances frontend..."
        cd frontend
        # S'assurer que nvm est chargé pour npm
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        npm install
        cd ..
    fi
    
    echo "Démarrage du frontend sur http://localhost:3000"
    cd frontend
    # S'assurer que nvm est chargé pour npm
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "=== Projet démarré ==="
    echo "Backend:  http://localhost:5000 (PID: $BACKEND_PID)"
    echo "Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
else
    echo ""
    echo "=== Backend démarré ==="
    echo "Backend:  http://localhost:5000 (PID: $BACKEND_PID)"
    echo ""
    echo "Pour tester l'API backend:"
    echo "  curl http://localhost:5000/health"
fi

echo ""
echo "Appuyez sur Ctrl+C pour arrêter"
echo ""

# Attendre
wait
