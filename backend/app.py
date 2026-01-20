from flask import Flask, request, jsonify
from flask_cors import CORS
from modules.nlp import extract_infrastructure
from modules.terraform_gen import generate_terraform
from modules.security import validate_infrastructure

app = Flask(__name__)
CORS(app)

@app.route("/generate", methods=["POST"])
def generate():
    # Recupere le JSON de la requete
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                "error": "JSON invalide",
                "message": "Le corps de la requete doit etre un JSON valide"
            }), 400
    except Exception as e:
        return jsonify({
            "error": "JSON invalide",
            "message": f"{str(e)}"
        }), 400
    
    phrase = data.get("description", "").strip()

    # Validation : phrase non vide
    if not phrase:
        return jsonify({
            "error": "Description vide",
            "message": "Veuillez fournir une description d'infrastructure"
        }), 400
    
    # Log la phrase recue
    print(f"Phrase recue: {phrase}")
    
    # Extraction via Gemini
    infra = extract_infrastructure(phrase)

    # Generation Terraform securise
    terraform = generate_terraform(infra)

    # Validation securite complete
    security = validate_infrastructure(phrase, terraform)

    # Decision finale
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


@app.route("/health", methods=["GET"])
def health():
    # Endpoint de monitoring
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    print("Backend Flask demarre sur http://localhost:5000")
    app.run(debug=True, port=5000)