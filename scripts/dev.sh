#!/bin/bash

# Script pour lancer backend et frontend en parallèle

set -e

# Couleurs pour les logs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Lancement du projet${NC}"

# Fonction pour nettoyer les processus à la sortie
cleanup() {
    echo ""
    echo "Arrêt des processus..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Lancer backend
echo -e "${BLUE}Backend:${NC} Démarrage sur http://localhost:5000"
cd backend
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
python app.py &
BACKEND_PID=$!
cd ..

# Attendre un peu que le backend démarre
sleep 2

# Lancer frontend
echo -e "${BLUE}Frontend:${NC} Démarrage sur http://localhost:3000"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}Backend et frontend lancés${NC}"
echo "Backend: http://localhost:5000 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter"

# Attendre que les processus se terminent
wait
