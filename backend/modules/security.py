from .security_rules import check_terraform_security


def detect_dangerous_requests(description: str) -> list:
    """
    Detecte si l'utilisateur demande quelque chose qui viole les regles de securite
    Retourne une liste de demandes dangereuses detectees
    """
    warnings = []
    d = description.lower()
    
    # Detection : DB publique
    if any(keyword in d for keyword in ["publique", "public", "accessible internet"]):
        if any(db in d for db in ["database", "db", "base", "mysql", "postgresql"]):
            warnings.append({
                "requested": "Base de donnees publique",
                "applied": "Base de donnees PRIVEE (politique de securite)",
                "reason": "Les bases de donnees ne doivent jamais etre accessibles depuis Internet"
            })
    
    # Detection : Pas de chiffrement
    if any(keyword in d for keyword in ["sans chiffrement", "non chiffre", "unencrypted"]):
        warnings.append({
            "requested": "Donnees non chiffrees",
            "applied": "Chiffrement ACTIVE (politique de securite)",
            "reason": "Le chiffrement est obligatoire pour proteger les donnees sensibles"
        })
    
    # Detection : SSH ouvert a tous
    if any(keyword in d for keyword in ["ssh 0.0.0.0", "ssh public", "ssh ouvert"]):
        warnings.append({
            "requested": "SSH ouvert a tous",
            "applied": "SSH RESTREINT (politique de securite)",
            "reason": "SSH ne doit etre accessible que depuis des IPs specifiques"
        })
    
    return warnings


def validate_infrastructure(description: str, terraform_code: str) -> dict:
    """
    Validation complete : detection proactive + verification code genere
    Retourne un verdict binaire (OK/NOT_OK) avec details
    """
    # Etape 1 : Detection proactive des demandes dangereuses
    dangerous_requests = detect_dangerous_requests(description)
    
    # Etape 2 : Verification du code Terraform genere
    security_report = check_terraform_security(terraform_code)
    
    # Etape 3 : Decision binaire
    # Blocage si :
    # - Demandes dangereuses detectees OU
    # - Score de securite < 70
    if dangerous_requests or security_report['security_score'] < 70:
        return {
            "status": "NOT_OK",
            "dangerous_requests": dangerous_requests,
            "violations": security_report.get('violations', []),
            "score": security_report['security_score'],
            "grade": security_report['security_grade']
        }
    
    return {
        "status": "OK",
        "score": security_report['security_score'],
        "grade": security_report['security_grade']
    }