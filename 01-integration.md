# Technical Journal

**Documentation de l'intégration progressive des composants du PoC.**

En combinant :

- L'interface de Nesrine : [https://github.com/OUALINes/PFE](https://github.com/OUALINes/PFE)
- La génération JSON d'Arlette (ZIP envoyé)
- La sécurité de Bilal : [https://github.com/bilalgu/pfe-multicloud-planner](https://github.com/bilalgu/pfe-multicloud-planner) et 
- Le backend Terraform de Sira : [https://github.com/ARISAWSS/Plannificateur-multicloud](https://github.com/ARISAWSS/Plannificateur-multicloud)

---
## 1. Configuration initiale de l'UI (Nesrine)

Clone et lancement de l'interface Next.js :

```bash
git clone https://github.com/OUALINes/PFE ui-nesrine
cd ui-nesrine
npm install
npm run dev
```

Port 3000 occupé (c'est mon laptop à moi), Next.js bascule sur le port 3001.

**Vérification :**

```
http://localhost:3001
```

Message console attendu : "Besoin saisi : Créer une base de données privée"

Résultat : validation de l'input texte UI.

---

## 2. Intégration du composant IA (Arlette)

Extraction du module IA :

```bash
unzip Projet_PFE.zip
```

### Adaptations

Modification de `test.py` pour :

- Accepter la phrase utilisateur en argument CLI
- Retourner uniquement du JSON et pas d'autre texte

Changements appliqués :

```python
import sys

if len(sys.argv) < 2:
    print("Erreur: Fournir une phrase utilisateur en argument.")
    exit(1)

user_query = sys.argv[1]
```

### Installation SDK Gemini

```bash
python3 -m venv pfe-planner
source pfe-planner/bin/activate
pip install google-genai python-dotenv
```

### Tests IA

```bash
python3 test.py "Créer une base de données privée"
```

Sortie initiale :

```json
{
  "provider": "aws",
  "region": "eu-west-3",
  "resources": {
    "compute": 1,
    "database": 1
  }
}
```

Problème : JSON incompatible avec les règles de sécurité.

---

## 3. Alignement du schéma JSON avec la politique de sécurité (Bilal)

Modifications du `json_schema` dans `test.py` :

- `database` passe de integer à object
- Ajout du champ `publicly_accessible` (boolean)

Nouvelle sortie IA :

```json
{
  "provider": "aws",
  "region": "eu-west-1",
  "resources": {
    "compute": 1,
    "database": {
      "publicly_accessible": false
    }
  }
}
```

---

## 4. Pipeline de sécurité : JSON --> check.py

Test positif :

```bash
python3 test.py "Créer une base de données privée" > output.json
python3 ../check.py output.json
# Sortie : OK : la base de donnees n'est pas publique
```

Test négatif :

```bash
python3 test.py "Créer une base de données publique" > output_bad.json
python3 ../check.py output_bad.json
# Sortie : NOT OK: la base de donnees est publique (interdit)
```

---

## 5. Connexion UI vers IA via API Next.js

Le projet utilise App Router, routes API dans `app/api/.../route.ts` (pas `pages/api`).

Création endpoint API :

```bash
mkdir -p ui-nesrine/app/api/gen
```

création du fichier `ui-nesrine/app/api/gen/route.ts`

**Vérification :**

```
http://localhost:3001/api/gen?phrase=Créer%20une%20base%20de%20données%20privée
```

Sortie obtenue :

```json
{"provider":"aws","region":"eu-west-3","resources":{"compute":1,"database":{"publicly_accessible":false},"webserver_type":"t2.micro"}}
```

Résultat : UI --> API --> Python --> JSON --> UI validé, aucune intervention CLI manuelle nécessaire.

---

## 6. Appel API depuis l'UI

Création d'un état pour afficher le JSON généré :

```tsx
const [infraJson, setInfraJson] = useState('');
```

Mise à jour de `handleGenerate()` avec ajout du `fetch()` vers l'API :

```tsx
const response = await fetch(`/api/gen?phrase=${encodeURIComponent(need)}`);
const data = await response.json();
setInfraJson(JSON.stringify(data));
```

Affichage UI :

```tsx
{ infraJson && <p>{ infraJson }</p> }
```

**Vérification :**

Résultat visible dans l'interface :

```
JSON :
{"provider":"aws","region":"eu-west-3","resources":{"compute":1,"database":{"publicly_accessible":false}}}
```

Résultat : UI --> API --> JSON Gemini opérationnel sans intervention terminal.

---

## 7. Intégration de la sécurité dans l'API

Ajout de `check.py` dans `route.ts` (App Router Next.js).

Écriture JSON temporaire et appel Python :

```ts
import fs from "fs";

const tmpJson = "/tmp/test-security.json";
fs.writeFileSync(tmpJson, JSON.stringify(json));

const checkScriptPath = "/home/bilal/Git/pfe-multicloud-planner/check.py";

try {
  const { stdout } = await execPromise(
    `${pythonPath} ${checkScriptPath} ${tmpJson}`
  );
  console.log("Résultat check.py :", stdout);
} catch (error) {
  console.error("Erreur Sécurité :", error);
}
```

**Vérification :**

Logs serveur :

```
Résultat check.py : OK : la base de donnees n'est pas publique
Résultat check.py : NOT OK: la base de donnees est publique (interdit)
```

Résultat : sécurité exécutée côté backend, cas positif et négatif validés.

---

## 8. Retour combiné JSON + Sécurité à la UI

Modification retour final de l'API :

```ts
return NextResponse.json({
  json,
  security: secOut.trim()
});
```

**Vérification :**

API renvoie maintenant :

```json
{
  "json": { ... },
  "security": "NOT OK: la base de donnees est publique (interdit)"
}
```

Résultat : le backend renvoie architecture + sécurité, pipeline DevSecOps end-to-end opérationnel.

---

## 9. Affichage sécurité dans l'UI

Nouvel état React pour la règle :

```tsx
const [securityResult, setSecurityResult] = useState("");
```

Affichage dans l'interface :

```tsx
<p>Sécurité : {securityResult}</p>
```

**Vérification :**

Résultat visuel final :

```
JSON :
{"provider":"aws","region":"eu-west-3", ... }
Sécurité :
OK : la base de donnees n'est pas publique
```

Résultat : expérience utilisateur complète, risque visible en temps réel.

---

## 10. Intégration du backend Terraform (Sira)

Clonage du backend existant :

```bash
git clone https://github.com/ARISAWSS/Plannificateur-multicloud.git backend-sira
```

Extraction de la fonction `generate_terraform_code()` dans un nouveau fichier dédié : `generate_tf.py`.

---

## 11. Alignement du JSON avec le pipeline

Pipeline produit :

```json
{
  "provider": "aws",
  "region": "eu-west-1",
  "resources": {
    "compute": 1,
    "database": {
      "publicly_accessible": false
    }
  }
}
```

Adaptations du code Terraform :

- `compute` remplace `servers`
- `database` devient un objet (pas un nombre)
- Gestion du champ `publicly_accessible`

Résultat : Terraform syntaxiquement valide.

---

## 12. Test local Terraform

```bash
python3 generate_tf.py test.json > main.tf
terraform init
terraform validate
```

**Vérification :**

```
Success! The configuration is valid.
```

Résultat : chaîne validée JSON --> Terraform --> Terraform valide.

---

## 13. Automatisation dans l'API Next.js

Ajout dans `api/gen/route.ts` après check sécurité :

```ts
if (secOut.includes("OK")) {
  console.log("Sécurité validée → Génération Terraform...");
  const tfScriptPath = "/home/bilal/Git/pfe-multicloud-planner/backend-sira/generate_tf.py";
  const { stdout: tfOut } = await execPromise(
    `${pythonPath} ${tfScriptPath} ${tmpJson}`
  );
  console.log(tfOut);
}
```

Résultat : Terraform déclenché automatiquement, fichier généré dans `/tmp/main.tf`.

---

## État actuel

**Pipeline validé :**

```
Utilisateur
  --> UI Next.js
  --> API Next.js
  --> IA Gemini (JSON)
  --> Check Sécurité
  --> Génération Terraform (si OK) #Quand sécurité faux génére quand meme (verif)
  --> /tmp/main.tf
```
