# PoC - Planificateur d'architectures sécurisées multi-cloud

## Objectif

Générer automatiquement une infrastructure Terraform sécurisée à partir d'une phrase en langage naturel, avec un garde-fou sécurité qui bloque les demandes dangereuses.

---

## Pipeline

```
Phrase utilisateur → Next.js → Flask → NLP → Terraform Gen → Security → Response
```

---

## Structure du projet

```
pfe-multicloud-planner/
├── backend/
│   ├── modules/
│   │   ├── nlp.py
│   │   ├── terraform_gen.py
│   │   ├── security_rules.py
│   │   └── security.py
│   ├── app.py
│   ├── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── api/generate/
│   │   │   └── route.ts
│   │   └── page.tsx
│   └── package.json
```

---

## Installation et lancement

### Méthode rapide (recommandée)

```bash
# Setup automatique complet
make setup

# Lancer backend et frontend en parallèle
make dev
```

Ou avec le script shell :
```bash
./scripts/setup.sh
./scripts/dev.sh
```

### Méthode manuelle

#### Backend Flask

```bash
cd backend

# Créer environnement virtuel Python
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installation des dépendances
pip install -r requirements.txt

# Configurer clé API Gemini dans .env
cp .env.example .env
# Éditer .env et ajouter GEMINI_API_KEY ou mettre AI_MODE=mock

# Lancement
python app.py
```

Backend disponible sur `http://localhost:5000`

#### Frontend Next.js

```bash
cd frontend

# Installation
npm install

# Lancement
npm run dev
```

Frontend disponible sur `http://localhost:3000` (ou :3001 si port occupé)

### Commandes Make disponibles

```bash
make help           # Afficher toutes les commandes
make setup          # Setup complet (backend + frontend)
make install        # Installer toutes les dépendances
make dev            # Lancer backend et frontend
make test           # Lancer tous les tests
make clean          # Nettoyer fichiers générés
```

**Documentation détaillée** : Voir `backend/README.md` et `CONTRIBUTING.md`

---

## Utilisation

1. Ouvrir `http://localhost:3000`
2. Saisir un besoin d'infrastructure en langage naturel
3. Cliquer sur "Générer l'infra"

### Exemples

**Cas OK** :

```
Je veux 2 serveurs web sur AWS
```

Résultat : Infrastructure générée avec succès + code Terraform

**Cas bloqué** :

```
Je veux une base de données publique
```

Résultat : Génération bloquée pour raisons de sécurité + justification

---

## Multi-cloud supporté

- AWS (testé)
- GCP (testé)
- Azure (règles limitées)
- OpenStack (non testé)

---

## Documentation

- `backend/README.md` : Documentation backend complète (API, endpoints, politiques sécurité)
- `backend/TESTS.md` : Scénarios de test validés avec curl
- `CONTRIBUTING.md` : Guide de contribution et développement
- `BACKLOG.md` : Améliorations futures

## Alternatives à Docker

Le projet utilise des environnements virtuels Python et npm pour le développement local :
- **Backend** : venv Python (géré automatiquement par `make`)
- **Frontend** : npm (géré automatiquement)
- **Scripts** : Makefile et scripts shell pour automatisation

Les fichiers Docker sont disponibles dans `docker-optional/` pour ceux qui préfèrent Docker.