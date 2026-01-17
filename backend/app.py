from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/generate", methods=["POST"])
def generate():
    # Recupere le JSON de la requete
    data = request.get_json()
    phrase = data.get("description", "")
    
    # Log la phrase recue
    print(f"Phrase recue: {phrase}")
    
    # Retourne un JSON hardcode pour tester
    return jsonify({
        "json": {
            "provider": "aws",
            "servers": 1,
            "databases": 0
        },
        "security": "OK",
        "terraform": "Terraform code"
    })

@app.route("/health", methods=["GET"])
def health():
    # Endpoint de monitoring
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    print("Backend Flask demarre sur http://localhost:5000")
    app.run(debug=True, port=5000)
