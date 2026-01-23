import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from modules.nlp import extract_infrastructure
from modules.terraform_gen import generate_terraform
from modules.security import validate_infrastructure

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Rate limiting: 10 requêtes par minute par IP
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["10 per minute"],
    storage_uri="memory://"
)

# Journal des runs (in-memory, peut être remplacé par Redis/DB en production)
runs_history = []
MAX_HISTORY_SIZE = 100

def log_run(phrase: str, infra: dict, security: dict, terraform_status: str):
    """Enregistre un run dans l'historique"""
    run = {
        "timestamp": datetime.now().isoformat(),
        "phrase": phrase[:200],  # Limite taille
        "infra": infra,
        "security_status": security.get("status"),
        "terraform_status": terraform_status,
        "security_score": security.get("score", 0)
    }
    runs_history.append(run)
    # Garder seulement les N derniers runs
    if len(runs_history) > MAX_HISTORY_SIZE:
        runs_history.pop(0)
    
    # Sauvegarder dans fichier (optionnel)
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/history.json", "w") as f:
            json.dump(runs_history[-50:], f, indent=2)  # Garder 50 derniers
    except Exception as e:
        logger.warning(f"Impossible de sauvegarder l'historique: {e}")


@app.route("/generate", methods=["POST"])
@limiter.limit("10 per minute")
def generate():
    """
    Génère une infrastructure Terraform sécurisée à partir d'une description.
    
    Returns:
        JSON avec:
        - json: Structure d'infrastructure extraite
        - security: "OK" ou "NOT_OK"
        - terraform: Code Terraform ou "BLOCKED"
        - security_report: Rapport détaillé de sécurité
    """
    try:
        # Récupère le JSON de la requête
        try:
            data = request.get_json()
            if data is None:
                return jsonify({
                    "error": "JSON invalide",
                    "message": "Le corps de la requête doit être un JSON valide"
                }), 400
        except Exception as e:
            logger.error(f"Erreur parsing JSON: {e}")
            return jsonify({
                "error": "JSON invalide",
                "message": f"Erreur de parsing: {str(e)}"
            }), 400
        
        phrase = data.get("description", "").strip()

        # Validation : phrase non vide
        if not phrase:
            return jsonify({
                "error": "Description vide",
                "message": "Veuillez fournir une description d'infrastructure"
            }), 400
        
        logger.info(f"Génération demandée: '{phrase[:100]}...'")
        
        # Extraction via Gemini (ou mock)
        try:
            infra = extract_infrastructure(phrase)
        except ValueError as e:
            logger.error(f"Erreur extraction infrastructure: {e}")
            return jsonify({
                "error": "Erreur extraction infrastructure",
                "message": str(e)
            }), 422
        except Exception as e:
            logger.error(f"Erreur inattendue extraction: {e}")
            return jsonify({
                "error": "Erreur serveur",
                "message": "Erreur lors de l'extraction de l'infrastructure"
            }), 500

        # Génération Terraform sécurisée
        try:
            terraform = generate_terraform(infra)
        except Exception as e:
            logger.error(f"Erreur génération Terraform: {e}")
            return jsonify({
                "error": "Erreur génération Terraform",
                "message": f"Impossible de générer le code Terraform: {str(e)}"
            }), 500

        # Validation sécurité complète
        try:
            security = validate_infrastructure(phrase, terraform)
        except Exception as e:
            logger.error(f"Erreur validation sécurité: {e}")
            return jsonify({
                "error": "Erreur validation sécurité",
                "message": f"Erreur lors de la validation: {str(e)}"
            }), 500

        # Journalisation
        terraform_status = "BLOCKED" if security["status"] == "NOT_OK" else "GENERATED"
        log_run(phrase, infra, security, terraform_status)

        # Décision finale
        if security["status"] == "NOT_OK":
            return jsonify({
                "json": infra,
                "security": "NOT_OK",
                "terraform": "BLOCKED",
                "security_report": security
            })
        
        return jsonify({
            "json": infra,
            "security": "OK",
            "terraform": terraform,
            "security_report": security
        })
    
    except Exception as e:
        logger.exception(f"Erreur inattendue dans /generate: {e}")
        return jsonify({
            "error": "Erreur serveur",
            "message": "Une erreur inattendue s'est produite"
        }), 500


@app.route("/health", methods=["GET"])
def health():
    """Endpoint de monitoring"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "history_size": len(runs_history)
    })


@app.route("/api/history", methods=["GET"])
def get_history():
    """Retourne l'historique des derniers runs"""
    limit = request.args.get("limit", 10, type=int)
    return jsonify({
        "runs": runs_history[-limit:],
        "total": len(runs_history)
    })


@app.errorhandler(429)
def ratelimit_handler(e):
    """Gestion des erreurs de rate limiting"""
    return jsonify({
        "error": "Trop de requêtes",
        "message": "Limite de 10 requêtes par minute atteinte. Veuillez réessayer plus tard."
    }), 429


if __name__ == "__main__":
    logger.info("Backend Flask démarre sur http://localhost:5000")
    app.run(debug=True, port=5000)