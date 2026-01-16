# test.py 

import sys
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Charge les variables du fichier .env
load_dotenv() 

# 1. Initialise le client Gemini
try:
    # Récupère la clé API Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("La variable GEMINI_API_KEY n'est pas définie dans le fichier .env")
        
    client = genai.Client(api_key=api_key)
except Exception as e:
    sys.stderr.write(f"Error: cannot init Gemini client: {e}\n")
    sys.exit(1)

# 2. Le PROMPT SYSTÈME et la structure JSON (modèle de donnée)
# Nous allons utiliser un "schema" pour forcer la structure du JSON.

# Définition précise du format JSON attendu
json_schema = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "provider": types.Schema(type=types.Type.STRING, description="Le fournisseur cloud : 'aws', 'azure', 'gcp', ou 'openstack'"),
        "region": types.Schema(type=types.Type.STRING, description="La région de déploiement (ex: 'eu-west-3')"),
        "resources": types.Schema(
            type=types.Type.OBJECT,
            properties={
                "compute": types.Schema(type=types.Type.INTEGER, description="Le nombre de serveurs/VMs requis"),
                "database": types.Schema(
                    type=types.Type.OBJECT, properties={
                        "publicly_accessible": types.Schema(type=types.Type.BOOLEAN, description="Base de données accessible depuis Internet ?")
                    },
                    description="Configuration de la base de données"),
                "webserver_type": types.Schema(type=types.Type.STRING, description="Le type d'instance du serveur (ex: 't2.micro', 'small')")
            },
            required=["compute", "database"]
        )
    },
    required=["provider", "region", "resources"]
)


# Instructions pour le modèle
SYSTEM_INSTRUCTIONS = (
    "Tu es un expert en traduction de demande d'infrastructure. "
    "Ton unique but est de générer un objet JSON valide qui respecte scrupuleusement le schéma de données fourni."
    "TU NE DOIS RÉPONDRE QU'AVEC L'OBJET JSON."
)

# 3. La PHRASE DE L'UTILISATEUR
# user_query = "Je veux deux serveurs web t2.micro et une base de données dans la région Paris (eu-west-3) d'AWS."
if len(sys.argv) < 2:
    print("Erreur: Fournir une phrase utilisateur en argument.")
    exit(1)

user_query = sys.argv[1]


def generate_infra_json(query, system_prompt, schema):
    # print(f"-> Requête utilisateur : {query}")
    try:
        # Configuration des paramètres pour forcer le JSON
        config = types.GenerateContentConfig(
            # Force la réponse à être un JSON
            response_mime_type="application/json",
            # Fournit le schéma pour garantir la structure interne
            response_schema=schema,
            system_instruction=system_prompt
        )
        
        # Appel à l'API Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Un modèle rapide et très bon pour le JSON
            contents=[query],
            config=config,
        )
        
        json_string = response.text
        return json.loads(json_string) # Transforme la chaîne JSON en objet Python (dictionnaire)

    except Exception as e:
        sys.stderr.write("Error: Gemini API call failed or invalid JSON output\n")
        sys.stderr.write(f"{e}\n")
        sys.exit(1)

# 4. Exécution
result = generate_infra_json(user_query, SYSTEM_INSTRUCTIONS, json_schema)
print(json.dumps(result, indent=2))
