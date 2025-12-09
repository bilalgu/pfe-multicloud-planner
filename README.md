# PoC - Planificateurs multi-niveaux d’architectures

## Pipeline du PoC

```
Phrase --> IA (Gemini) --> JSON --> Sécurité (Python) --> Terraform (Python) --> Fichier main.tf
```

## Objectif

Générer automatiquement une infrastructure AWS à partir d'une phrase utilisateur avec un garde-fou sécurité.

---

## Structure du projet

```
pfe-multicloud-planner/
├── backend/
│   ├── check.py           # Sécurité (Bilal)
│   ├── generate_tf.py     # Génération Terraform (Sira)
│   └── test.py            # IA Gemini (Arlette)
├── frontend/              # UI Next.js (Nesrine)
├── .env
└── README.md
```

---

## Lancer le PoC

### Backend Python (IA + Sécurité + Terraform)

```bash
python3 -m venv pfe-planner
source pfe-planner/bin/activate
pip install google-genai python-dotenv
```

Configurer la clé API Gemini :

```bash
cat .env
# GEMINI_API_KEY="VOTRE_CLÉ_ICI"
```

Remplacer les chemins dans `frontend/app/api/gen/route.ts` (ligne 15 et 41) :

```bash
realpath backend/test.py           # --> TEST_SCRIPT_PATH
realpath backend/check.py          # --> CHECK_SCRIPT_PATH
realpath backend/generate_tf.py    # --> TF_SCRIPT_PATH
echo "$(pwd)/pfe-planner/bin/python3"  # --> PYTHON_PATH
```

### Frontend Next.js (UI)

```bash
cd frontend/
npm install
npm run dev
```

Ouvrir :

```
http://localhost:3000
```

(ou :3001 si 3000 occupé)

---

## Exemple d'utilisation

Entrée dans l'UI :

```
Créer une base de données privée
```

**Résultat attendu dans l'UI :**

```
Ton besoin :
Créer une base de données privée

JSON :
{"provider":"aws","region":"eu-west-1","resources": ... }

Sécurité :
OK : la base de donnees n'est pas publique
```

**Logs navigateur (DevTools) :**

```json
{
  "json": {...},
  "security": "OK : la base de donnees n'est pas publique",
  "terraform": "GENERATED"
}
```

**Logs terminal (Next.js) :**

```
Sécurité validée --> Génération Terraform...
Terraform généré dans /tmp/main.tf
```

**Vérifier le fichier généré :**

```bash
ls -lh /tmp/main.tf
head /tmp/main.tf
grep publicly_accessible /tmp/main.tf
```

---

## Exemple de blocage sécurité

Entrée :

```
Créer une base de données publique
```

Résultat attendu : pas de génération Terraform (blocage sécurité).

**Note :** actuellement le blocage n'est pas implémenté dans `frontend/app/api/gen/route.ts`, à corriger.
