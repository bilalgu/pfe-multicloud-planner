#  Planificateur Multi-Cloud d'Infrastructures Sécurisées

Description

 planificateur d'architecture multi-niveaux qui :
-  Comprend le langage naturel via Google Gemini AI
-  Supporte 4 providers cloud (AWS, Azure, GCP, OpenStack)
-  Applique 6 règles de sécurité automatiquement
-  Génère du code Terraform (Infrastructure as Code)
-  Génère du code Ansible (Configuration Management)
- Protège contre les configurations dangereuses

---

# Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    1. EXPRESSION DES BESOINS                │
│  User Input (NLP) → Gemini AI → Infrastructure JSON        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              2. BIBLIOTHÈQUE DE POLITIQUES                  │
│  security_rules.py → 6 règles → Paramètres sécurisés       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 3. MOTEURS IA/IAC                           │
│  ├─ Terraform Generator (IaC)                              │
│  └─ Ansible Generator (Configuration)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              4. CODE SÉCURISÉ + VALIDATION                  │
│  Terraform Code + Ansible Playbook + Security Report       │
└─────────────────────────────────────────────────────────────┘
#  Fonctionnalités

#  Intelligence Artificielle
- Gemini AI pour la compréhension du langage naturel
- Fallback si l'API est indisponible
- Extraction des besoins en JSON

# Multi-Cloud
- AWS : EC2, VPC, Security Groups
- Azure : Virtual Machines, MySQL, VNet, NSG
- GCP: Compute Engine, Cloud SQL, VPC, Firewall
- OpenStack : Instances, DB, Network, Security Groups

# Sécurité (6 règles automatiques)
| # | Règle | Sévérité | Description |
|---|-------|----------|-------------|
| 1 | Base de données privée   | HIGH  | Jamais accessible publiquement   |
| 2 | Chiffrement au repos     | HIGH  | Volumes et DB chiffrés           |
| 3 | SSL/TLS obligatoire      | HIGH  | Connexions sécurisées            |
| 4 | Surveillance active      | MEDIUM| Logs et monitoring               |
| 5 | Sauvegardes automatiques | MEDIUM| Rétention 7 jours               |
| 6 | Pas de credentials hardcodés | CRITICAL | Variables sensibles       |

Score de sécurité : A (90-100) | B (75-89) | C (60-74) | D (0-59)

# 📦 Génération de code
- Terraform : Infrastructure as Code multi-cloud
- Ansible : Configuration automatisée (firewall, MySQL, Nginx)
- Toggle interface : Passer facilement entre Terraform et Ansible
- Téléchargement : Fichiers `.tf` et `.yml` prêts à l'emploi


 📁 Structure du projet

pfe-multicloud-planner/
├── backend/
│   ├── app.py                    #  Backend Flask unifié 
│   ├── security_rules.py         #  6 règles de sécurité 
│   ├── requirements.txt          #  Dépendances Python
│   ├── .env                      #  Template configuration Clé API Gemini
│   
├── frontend/
│   └── app/
│       ├── page.tsx              #  Interface Next.js avec toggle
│       └── api/
│           └── generate/
│               └── route.ts      #  Proxy vers Flask
├── .gitignore
├── README.md
└── CHANGELOG.md                  # 📝 Historique des versions


# Installation

# Prérequis
- Python 3.10+
- Node.js 18+
- Clé API Google Gemini ([Obtenir une clé](https://ai.google.dev/))

# Backend

# Créer environnement virtuel
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env et ajouter :
# GEMINI_API_KEY=votre_cle_api_ici


### Frontend

cd frontend
npm install


 Utilisation

 Lancer le backend

cd backend
python app.py
# → Backend sur http://localhost:5000


 Lancer le frontend

cd frontend
npm run dev
 → Interface sur http://localhost:3000


 Tester l'application

1. Ouvrir http://localhost:3000
2. Entrer une description, par exemple :

   Je veux 2 serveurs AWS avec une base de données MySQL

3. Cliquer sur "Générer l'infra"
4. Voir :
   -  Infrastructure détectée (cards colorées)
   -  Code Terraform généré
   -  Toggle vers Ansible
   - Score de sécurité (100/100)
   -  Télécharger `.tf` et `.yml`


 Exemple 1 : Serveur simple

Input :

Un serveur web AWS


Output :
- 1 instance EC2 t2.micro
- VPC privé
- Security group (HTTPS uniquement)
- Configuration Nginx via Ansible



 Exemple 2 : Application complète

Input :

Je veux 3 serveurs Azure avec une base de données MySQL


Output :
- 3 VMs Azure Standard
- MySQL Server sécurisé (privé, SSL, backups)
- VNet isolé
- Configuration complète via Ansible



 Évolution du projet

 v1.0 - PoC Initial

test.py (Gemini) → check.py (Sécurité) → generate_tf.py (Terraform)


v2.0 - Architecture unifiée (Actuel)

app.py (Backend unifié) + security_rules.py (Module sécurité)


Raisons du refactoring :
-  Simplification 
-  Moins de conflits Git
-  Ajout de nouvelles fonctionnalités (Ansible, multi-cloud)



Équipe

- Arlette : API IA Gemini (NLP)
- Bilal :   Sécurité (Règles)
- Sira :    Backend + Terraform
- Nesrine : Interface Next.js
- Mariam :  Architecture unifiée + Ansible



 Documentation supplémentaire

- [Backend README](./backend/README.md) - Documentation technique backend
- [CHANGELOG.md](./CHANGELOG.md) - Historique des versions
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Guide de contribution (à créer)



Liens utiles

- [Google Gemini AI](https://ai.google.dev/)
- [Terraform Documentation](https://developer.hashicorp.com/terraform)
- [Ansible Documentation](https://docs.ansible.com/)



