import os
import json
import logging
import threading
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, field_validator
from contextlib import contextmanager

load_dotenv()

# Configuration logging
logger = logging.getLogger(__name__)

# Mode mock pour développement
AI_MODE = os.getenv("AI_MODE", "real").lower()

# Initialise le client Gemini (seulement si mode réel)
client = None
if AI_MODE == "real":
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY manquante dans .env")
    client = genai.Client(api_key=api_key)
elif AI_MODE == "mock":
    logger.info("Mode MOCK activé - utilisation de données fictives")

# Schema JSON structure - definit le format attendu par Gemini
# Format liste pour supporter mono et multi-cloud
json_schema = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "providers": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
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
        )
    },
    required=["providers"],
)

# Instructions pour Gemini - prompt system
SYSTEM_INSTRUCTIONS = (
    "Tu es un architecte cloud expert. "
    "Analyse EXACTEMENT la demande utilisateur et genere les composants demandes. "
    "\n\n"
    "MULTI-CLOUD:\n"
    "- Si plusieurs providers mentionnes -> retourne une liste avec chaque provider\n"
    "- Si un seul provider -> retourne une liste avec 1 element\n"
    "- Repartis les ressources selon la demande utilisateur\n"
    "\n"
    "REGLES STRICTES:\n"
    "- Si l'utilisateur ne mentionne PAS de base de donnees -> databases: 0\n"
    "- Si l'utilisateur ne mentionne PAS de load balancer -> load_balancers: 0\n"
    "- Ne JAMAIS rajouter de composants non demandes\n"
    "\n"
    "EXEMPLES:\n"
    "Demande: 'Je veux un serveur AWS' -> {providers: [{provider: 'aws', servers: 1, databases: 0, networks: 1, load_balancers: 0, security_groups: 1}]}\n"
    "Demande: '3 serveurs sur GCP + 2 serveurs sur AWS' -> {providers: [{provider: 'gcp', servers: 3, databases: 0, networks: 1, load_balancers: 0, security_groups: 1}, {provider: 'aws', servers: 2, databases: 0, networks: 1, load_balancers: 0, security_groups: 1}]}\n"
    "Demande: '3 serveurs avec MySQL' -> {providers: [{servers: 3, databases: 1, load_balancers: 0}]}\n"
)

# Modèle Pydantic pour validation - configuration par provider
class ProviderConfig(BaseModel):
    """Configuration pour un provider unique"""
    provider: str = Field(..., description="Provider cloud")
    servers: int = Field(ge=0, default=0, description="Nombre de serveurs")
    databases: int = Field(ge=0, default=0, description="Nombre de bases de données")
    networks: int = Field(ge=0, default=0, description="Nombre de réseaux")
    load_balancers: int = Field(ge=0, default=0, description="Nombre de load balancers")
    security_groups: int = Field(ge=0, default=0, description="Nombre de security groups")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        valid_providers = ['aws', 'azure', 'gcp', 'openstack']
        v_lower = v.lower()
        if v_lower not in valid_providers:
            logger.warning(f"Provider invalide '{v}', utilisation de 'aws' par défaut")
            return 'aws'
        return v_lower


class InfrastructureSchema(BaseModel):
    """Schéma de validation pour infrastructure mono ou multi-cloud"""
    providers: list[ProviderConfig] = Field(..., min_length=1, description="Liste des configurations par provider")
    
    class Config:
        json_schema_extra = {
            "example": {
                "providers": [
                    {
                        "provider": "gcp",
                        "servers": 3,
                        "databases": 0,
                        "networks": 1,
                        "load_balancers": 0,
                        "security_groups": 1
                    },
                    {
                        "provider": "aws",
                        "servers": 2,
                        "databases": 1,
                        "networks": 1,
                        "load_balancers": 0,
                        "security_groups": 1
                    }
                ]
            }
        }


# Timeout context manager (compatible multiplateforme)
class TimeoutError(Exception):
    """Exception levée lors d'un timeout"""
    pass


@contextmanager
def timeout(seconds: int):
    """Context manager pour timeout sur opérations (compatible multiplateforme)"""
    timer = None
    timeout_occurred = threading.Event()
    
    def timeout_handler():
        timeout_occurred.set()
    
    timer = threading.Timer(seconds, timeout_handler)
    timer.start()
    
    try:
        yield
    except Exception as e:
        if timeout_occurred.is_set():
            raise TimeoutError(f"Opération timeout après {seconds} secondes")
        raise
    finally:
        if timer:
            timer.cancel()
        if timeout_occurred.is_set():
            raise TimeoutError(f"Opération timeout après {seconds} secondes")


def mock_extract_infrastructure(description: str) -> dict:
    """Extraction mock pour développement sans API"""
    logger.info(f"Mode MOCK: extraction depuis '{description[:50]}...'")
    
    # Parser simple basé sur mots-clés
    desc_lower = description.lower()
    
    # Détection provider
    provider = "aws"
    if "azure" in desc_lower:
        provider = "azure"
    elif "gcp" in desc_lower or "google" in desc_lower:
        provider = "gcp"
    elif "openstack" in desc_lower:
        provider = "openstack"
    
    # Détection serveurs
    servers = 0
    for word in desc_lower.split():
        if word.isdigit():
            servers = int(word)
            break
    if servers == 0 and any(word in desc_lower for word in ["serveur", "server", "vm", "instance"]):
        servers = 1
    
    # Détection databases
    databases = 0
    if any(word in desc_lower for word in ["database", "db", "base", "mysql", "postgresql"]):
        databases = 1
    
    # Détection load balancers
    load_balancers = 0
    if any(word in desc_lower for word in ["load balancer", "loadbalancer", "lb"]):
        load_balancers = 1
    
    # Infrastructure minimale
    networks = 1 if servers > 0 or databases > 0 else 0
    security_groups = 1 if servers > 0 or databases > 0 else 0
    
    # Format liste pour compatibilité avec nouveau schéma
    return {
        "providers": [
            {
                "provider": provider,
                "servers": servers,
                "databases": databases,
                "networks": networks,
                "load_balancers": load_balancers,
                "security_groups": security_groups
            }
        ]
    }


def extract_infrastructure(description: str) -> dict:
    """
    Phrase utilisateur -> JSON structure via Gemini (ou mock)
    Retourne un dictionnaire validé avec liste de providers
    
    Args:
        description: Description de l'infrastructure en langage naturel
        
    Returns:
        dict: Structure d'infrastructure validée avec clé 'providers' (liste)
        
    Raises:
        ValueError: Si le JSON généré est invalide
        TimeoutError: Si l'appel Gemini dépasse le timeout
    """
    # Mode mock pour développement
    if AI_MODE == "mock":
        result = mock_extract_infrastructure(description)
        try:
            # Validation avec Pydantic
            validated = InfrastructureSchema(**result)
            return validated.model_dump()
        except Exception as e:
            logger.error(f"Erreur validation mode mock: {e}")
            raise ValueError(f"Erreur validation JSON mock: {str(e)}")
    
    # Mode réel avec Gemini
    if not client:
        raise ValueError("Client Gemini non initialisé")
    
    try:
        # Timeout de 30 secondes
        with timeout(30):
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
            candidate = response.candidates[0]
            
            if not candidate.content or not candidate.content.parts:
                raise ValueError("Reponse Gemini vide")

            part = candidate.content.parts[0]

            # Methode 1 : structured_data (objet Python direct)
            if hasattr(part, "structured_data") and part.structured_data:
                result = dict(part.structured_data)
            # Methode 2 : text (string JSON a parser)
            elif hasattr(part, "text") and part.text:
                result = json.loads(part.text)
            else:
                raise ValueError("Reponse Gemini inexploitable")
        
    except TimeoutError:
        logger.error("Timeout lors de l'appel Gemini (30s)")
        raise ValueError("Timeout: L'appel à l'IA a dépassé 30 secondes")
    except json.JSONDecodeError as e:
        logger.error(f"Erreur parsing JSON Gemini: {e}")
        raise ValueError(f"JSON invalide retourné par Gemini: {str(e)}")
    except Exception as e:
        logger.error(f"Erreur lors de l'appel Gemini: {repr(e)}")
        # Fallback vers mode mock en cas d'erreur
        logger.warning("Fallback vers mode mock")
        result = mock_extract_infrastructure(description)
    
    # Validation avec Pydantic
    try:
        validated = InfrastructureSchema(**result)
        result = validated.model_dump()
    except Exception as e:
        logger.error(f"Erreur validation JSON: {e}, données reçues: {result}")
        raise ValueError(f"Schéma JSON invalide: {str(e)}. Format attendu: {{'providers': [{{...}}]}}")
    
    # Normalisation des données pour chaque provider
    for provider_config in result["providers"]:
        # Si provider manquant ou invalide, force aws par defaut
        if not provider_config.get("provider") or provider_config.get("provider") == "null":
            provider_config["provider"] = "aws"

        # Assure infrastructure minimale complete
        # Un serveur necessite toujours un VPC et un security group
        if provider_config.get("servers", 0) > 0 or provider_config.get("databases", 0) > 0:
            provider_config["networks"] = max(provider_config.get("networks", 0), 1)
            provider_config["security_groups"] = max(provider_config.get("security_groups", 0), 1)
    
    logger.info(f"Infrastructure extraite: {result}")
    return result