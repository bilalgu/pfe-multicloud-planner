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

### Backend Flask

```bash
# Creer environnement virtuel Python (si pas encore fait)
python3 -m venv pfe-planner
source pfe-planner/bin/activate

cd backend

# Installation des dependances
pip install -r requirements.txt

# Configurer cle API Gemini dans .env
# Par defaut : GEMINI_API_KEY="VOTRE_CLE_ICI"
# Remplacer par votre vraie cle Gemini

# Lancement
python app.py
```

Backend disponible sur `http://localhost:5000`

**Documentation détaillée** : Voir `backend/README.md`

### Frontend Next.js

```bash
cd frontend

# Installation
npm install

# Lancement
npm run dev
```

Frontend disponible sur `http://localhost:3000` (ou :3001 si port occupé)

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

- AWS (✅ testé)
- GCP (✅ testé)
- Azure (⚠️ règles limitées)
- OpenStack (⚠️ non testé)

---

## Documentation

- `backend/README.md` : Documentation backend complète (API, endpoints, politiques sécurité)
- `backend/TESTS.md` : Scénarios de test validés avec curl
- `BACKLOG.md` : Améliorations futures