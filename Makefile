.PHONY: help install-backend install-frontend install dev-backend dev-frontend dev test-backend test-frontend clean setup

help:
	@echo "Commandes disponibles:"
	@echo "  make setup          - Setup complet (backend + frontend)"
	@echo "  make install        - Installer toutes les dépendances"
	@echo "  make install-backend - Installer dépendances backend"
	@echo "  make install-frontend - Installer dépendances frontend"
	@echo "  make dev            - Lancer backend et frontend en parallèle"
	@echo "  make dev-backend    - Lancer uniquement le backend"
	@echo "  make dev-frontend   - Lancer uniquement le frontend"
	@echo "  make test           - Lancer tous les tests"
	@echo "  make test-backend   - Lancer tests backend"
	@echo "  make test-frontend  - Lancer lint frontend"
	@echo "  make clean          - Nettoyer fichiers générés"

setup: install
	@echo "Setup terminé. Créez backend/.env depuis backend/.env.example"

install: install-backend install-frontend

install-backend:
	@echo "Installation backend..."
	@cd backend && \
	if [ ! -d "venv" ]; then \
		python3 -m venv venv; \
	fi && \
	. venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt
	@echo "Backend installé. Activez avec: source backend/venv/bin/activate"

install-frontend:
	@echo "Installation frontend..."
	@cd frontend && npm install
	@echo "Frontend installé"

dev:
	@echo "Lancement backend et frontend..."
	@make dev-backend & make dev-frontend

dev-backend:
	@echo "Lancement backend sur http://localhost:5000"
	@cd backend && \
	if [ ! -d "venv" ]; then \
		echo "Création venv..."; \
		python3 -m venv venv; \
		. venv/bin/activate && pip install -r requirements.txt; \
	fi && \
	. venv/bin/activate && \
	python app.py

dev-frontend:
	@echo "Lancement frontend sur http://localhost:3000"
	@cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	@echo "Tests backend..."
	@cd backend && \
	if [ ! -d "venv" ]; then \
		make install-backend; \
	fi && \
	. venv/bin/activate && \
	export AI_MODE=mock && \
	pytest tests/ -v

test-frontend:
	@echo "Lint frontend..."
	@cd frontend && npm run lint

clean:
	@echo "Nettoyage..."
	@find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	@find . -type d -name ".next" -exec rm -r {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -r {} + 2>/dev/null || true
	@rm -rf backend/venv 2>/dev/null || true
	@rm -rf backend/.coverage backend/htmlcov 2>/dev/null || true
	@echo "Nettoyage terminé"
