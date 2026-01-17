import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Initialise le client Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY manquante dans .env")

client = genai.Client(api_key=api_key)

# Schema JSON structure - definit le format attendu
json_schema = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "provider": types.Schema(
            type=types.Type.STRING,
            description="Provider cloud : aws, azure, gcp, openstack"
        ),
        "servers": types.Schema(
            type=types.Type.INTEGER,
            description="Nombre de serveurs/VMs"
        ),
        "databases": types.Schema(
            type=types.Type.INTEGER,
            description="Nombre de bases de donnees (0 si non mentionne)"
        ),
        "networks": types.Schema(
            type=types.Type.INTEGER,
            description="Nombre de reseaux"
        ),
        "load_balancers": types.Schema(
            type=types.Type.INTEGER,
            description="Nombre de load balancers (0 si non mentionne)"
        ),
        "security_groups": types.Schema(
            type=types.Type.INTEGER,
            description="Nombre de groupes de securite"
        ),
    },
    required=["provider", "servers", "databases", "networks", "load_balancers", "security_groups"],
)

# Instructions pour Gemini - prompt system
SYSTEM_INSTRUCTIONS = (
    "Tu es un architecte cloud expert. "
    "Analyse EXACTEMENT la demande utilisateur et genere UNIQUEMENT les composants explicitement demandes. "
    "\n\n"
    "REGLES STRICTES:\n"
    "- Si l'utilisateur ne mentionne PAS de base de donnees -> databases: 0\n"
    "- Si l'utilisateur ne mentionne PAS de load balancer -> load_balancers: 0\n"
    "- Ne JAMAIS rajouter de composants non demandes\n"
    "\n"
    "EXEMPLES:\n"
    "Demande: 'Je veux un serveur AWS' -> {servers: 1, databases: 0, load_balancers: 0}\n"
    "Demande: 'Je veux 3 serveurs avec MySQL' -> {servers: 3, databases: 1, load_balancers: 0}\n"
    "Demande: 'Une base de donnees' -> {servers: 0, databases: 1, load_balancers: 0}\n"
)


def extract_infrastructure(description: str) -> dict:
    """
    Phrase utilisateur -> JSON structure via Gemini
    Retourne un dictionnaire avec provider, servers, databases, etc.
    """
    try:
        # Configure Gemini pour forcer le format JSON
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=json_schema,
            system_instruction=SYSTEM_INSTRUCTIONS,
        )

        # Appel a Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[description],
            config=config,
        )

        # Extraction du JSON de la reponse Gemini
        # Gemini peut retourner le JSON de 2 façons differentes selon la version API
        candidate = response.candidates[0]
        
        if not candidate.content or not candidate.content.parts:
            raise ValueError("Reponse Gemini vide")

        part = candidate.content.parts[0]

        # Methode 1 : structured_data (objet Python direct)
        if hasattr(part, "structured_data") and part.structured_data:
            return dict(part.structured_data)

        # Methode 2 : text (string JSON a parser)
        if hasattr(part, "text") and part.text:
            return json.loads(part.text)

        raise ValueError("Reponse Gemini inexploitable")

    except Exception as e:
        # Fallback basique si Gemini echoue
        # Retourne une config AWS minimale par defaut
        print(f"Gemini fallback: {e}")
        return {
            "provider": "aws",
            "servers": 1,
            "databases": 0,
            "networks": 1,
            "load_balancers": 0,
            "security_groups": 1,
        }