"""
BIBLIOTHÈQUE DE GÉNÉRATION DE POLITIQUES DE SÉCURITÉ
6 règles essentielles pour le MVP
"""

import re
import logging

logger = logging.getLogger(__name__)

# ============================================
# POLITIQUES DE SÉCURITÉ (6 règles MVP)
# ============================================

SECURITY_POLICIES = {
    "db_no_public_ip": {
        "name": "Base de donnees privee",
        "description": "Les bases de donnees ne doivent jamais etre accessibles depuis Internet",
        "severity": "HIGH",
        "category": "Network Access",
        "terraform_settings": {
            "aws": {"publicly_accessible": False},
            "azure": {"public_network_access_enabled": False},
            "gcp": {"ipv4_enabled": False},
            "openstack": {"public": False}
        },
        "check": lambda code, provider=None: _check_db_no_public_ip(code, provider)
    },
    
    "encryption_at_rest": {
        "name": "Chiffrement au repos",
        "description": "Les donnees doivent etre chiffrees au repos",
        "severity": "HIGH",
        "category": "Encryption",
        "terraform_settings": {
            "aws": {"storage_encrypted": True, "encrypted": True},
            "azure": {"infrastructure_encryption_enabled": True},
            "gcp": {"disk_encryption_key": "customer-managed"},
            "openstack": {"encrypted": True}
        },
        "check": lambda code, provider=None: _check_encryption_at_rest(code, provider)
    },
    
    "ssl_required": {
        "name": "SSL/TLS obligatoire",
        "description": "Les connexions doivent utiliser SSL/TLS",
        "severity": "HIGH",
        "category": "Encryption",
        "terraform_settings": {
            "aws": {"require_ssl": True},
            "azure": {"ssl_enforcement_enabled": True, "ssl_minimal_tls_version_enforced": "TLS1_2"},
            "gcp": {"require_ssl": True},
            "openstack": {"ssl_required": True}
        },
        "check": lambda code, provider=None: _check_ssl_required(code, provider)
    },
    
    "monitoring_enabled": {
        "name": "Surveillance active",
        "description": "La surveillance et les logs doivent etre actives",
        "severity": "MEDIUM",
        "category": "Monitoring",
        "terraform_settings": {
            "aws": {"monitoring": True, "enabled_cloudwatch_logs_exports": ["error", "general", "slowquery"]},
            "azure": {"insights_enabled": True},
            "gcp": {"query_insights_enabled": True},
            "openstack": {"logging_enabled": True}
        },
        "check": lambda code, provider=None: _check_monitoring_enabled(code, provider)
    },
    
    "backup_enabled": {
        "name": "Sauvegardes automatiques",
        "description": "Les sauvegardes doivent etre configurees",
        "severity": "MEDIUM",
        "category": "Backup & Recovery",
        "terraform_settings": {
            "aws": {"backup_retention_period": 7},
            "azure": {"backup_retention_days": 7},
            "gcp": {"backup_enabled": True, "backup_start_time": "03:00"},
            "openstack": {"backup_enabled": True}
        },
        "check": lambda code, provider=None: "backup" in code.lower()
    },
    
    "no_hardcoded_credentials": {
        "name": "Pas de credentials en dur",
        "description": "Les mots de passe ne doivent jamais etre hardcodes",
        "severity": "CRITICAL",
        "category": "Identity & Access",
        "terraform_settings": {
            "description": "Utiliser des variables sensibles"
        },
        "check": lambda code, provider=None: not any(
            pattern in code
            for pattern in ['password = "', 'secret = "', 'api_key = "']
        )
    }
}

# ============================================
# FONCTIONS DE VÉRIFICATION PAR PROVIDER
# ============================================

def _detect_provider(terraform_code: str) -> str:
    """Détecte le provider depuis le code Terraform"""
    code_lower = terraform_code.lower()
    if 'provider "aws"' in code_lower or 'hashicorp/aws' in code_lower:
        return "aws"
    elif 'provider "azurerm"' in code_lower or 'hashicorp/azurerm' in code_lower:
        return "azure"
    elif 'provider "google"' in code_lower or 'hashicorp/google' in code_lower:
        return "gcp"
    elif 'provider "openstack"' in code_lower:
        return "openstack"
    return "aws"  # Default


def _check_db_no_public_ip(code: str, provider: str = None) -> bool:
    """Vérifie que les bases de données ne sont pas publiques"""
    if provider is None:
        provider = _detect_provider(code)
    
    code_lower = code.lower()
    
    # Vérifications spécifiques par provider
    if provider == "aws":
        # AWS: publicly_accessible doit être false ou absent
        if "publicly_accessible = true" in code_lower:
            return False
        # Si DB présente, vérifier qu'elle est dans un VPC privé
        if "aws_db_instance" in code_lower:
            return "publicly_accessible = false" in code_lower or "vpc_security_group_ids" in code_lower
    elif provider == "azure":
        # Azure: public_network_access_enabled doit être false
        if "azurerm_mysql_server" in code_lower or "azurerm_postgresql_server" in code_lower:
            return "public_network_access_enabled = false" in code_lower
    elif provider == "gcp":
        # GCP: ipv4_enabled doit être false
        if "google_sql_database_instance" in code_lower:
            return "ipv4_enabled = false" in code_lower or "ipv4_enabled    = false" in code_lower
    
    # Si pas de DB, considérer comme OK
    db_keywords = ["db_instance", "mysql_server", "postgresql_server", "sql_database_instance"]
    if not any(keyword in code_lower for keyword in db_keywords):
        return True
    
    # Par défaut, si on ne peut pas vérifier, on considère comme OK (pas de DB publique explicite)
    return True


def _check_encryption_at_rest(code: str, provider: str = None) -> bool:
    """Vérifie le chiffrement au repos"""
    if provider is None:
        provider = _detect_provider(code)
    
    code_lower = code.lower()
    
    # Vérifications spécifiques par provider
    if provider == "aws":
        # AWS: encrypted = true ou storage_encrypted = true
        if "aws_instance" in code_lower or "aws_db_instance" in code_lower:
            return ("encrypted = true" in code_lower or 
                   "storage_encrypted = true" in code_lower or
                   "storage_encrypted   = true" in code_lower)
    elif provider == "azure":
        # Azure: infrastructure_encryption_enabled ou pas de mention (par défaut chiffré)
        if "azurerm_mysql_server" in code_lower or "azurerm_linux_virtual_machine" in code_lower:
            # Azure chiffre par défaut, donc OK si présent
            return True
    elif provider == "gcp":
        # GCP: disk_encryption_key ou chiffrement par défaut
        if "google_compute_instance" in code_lower or "google_sql_database_instance" in code_lower:
            # GCP chiffre par défaut
            return True
    
    # Si pas de ressources nécessitant chiffrement, OK
    return True


def _check_ssl_required(code: str, provider: str = None) -> bool:
    """Vérifie que SSL/TLS est requis"""
    if provider is None:
        provider = _detect_provider(code)
    
    code_lower = code.lower()
    
    # Vérifications spécifiques par provider
    if provider == "aws":
        # AWS: require_ssl = true
        if "aws_db_instance" in code_lower:
            return "require_ssl = true" in code_lower or "ssl" in code_lower
    elif provider == "azure":
        # Azure: ssl_enforcement_enabled = true
        if "azurerm_mysql_server" in code_lower or "azurerm_postgresql_server" in code_lower:
            return "ssl_enforcement_enabled = true" in code_lower or "ssl_minimal_tls_version" in code_lower
    elif provider == "gcp":
        # GCP: require_ssl = true
        if "google_sql_database_instance" in code_lower:
            return "require_ssl = true" in code_lower or "require_ssl  = true" in code_lower
    
    # Vérification générique
    if "ssl" in code_lower or "tls" in code_lower:
        return True
    
    # Si pas de DB, OK
    db_keywords = ["db_instance", "mysql_server", "postgresql_server", "sql_database_instance"]
    if not any(keyword in code_lower for keyword in db_keywords):
        return True
    
    return False


def _check_monitoring_enabled(code: str, provider: str = None) -> bool:
    """Vérifie que le monitoring est activé"""
    if provider is None:
        provider = _detect_provider(code)
    
    code_lower = code.lower()
    
    # Vérifications spécifiques par provider
    if provider == "aws":
        # AWS: monitoring = true ou enabled_cloudwatch_logs_exports
        if "aws_instance" in code_lower:
            return "monitoring = true" in code_lower
        if "aws_db_instance" in code_lower:
            return "enabled_cloudwatch_logs_exports" in code_lower or "monitoring" in code_lower
    elif provider == "azure":
        # Azure: insights ou monitoring
        return "insights" in code_lower or "monitoring" in code_lower
    elif provider == "gcp":
        # GCP: query_insights_enabled ou monitoring
        return "query_insights_enabled" in code_lower or "monitoring" in code_lower or "insights" in code_lower
    
    # Vérification générique
    return "monitoring" in code_lower or "logs" in code_lower or "insights" in code_lower


# ============================================
# FONCTION : Obtenir les paramètres sécurisés
# ============================================

def get_secure_settings(provider: str) -> dict:
    """
    Retourne les parametres securises pour un provider
    Fusionne toutes les politiques de securite applicables
    """
    settings = {}
    
    for policy in SECURITY_POLICIES.values():
        if "terraform_settings" in policy:
            provider_settings = policy["terraform_settings"].get(provider, {})
            if isinstance(provider_settings, dict):
                settings.update(provider_settings)
    
    return settings

# ============================================
# FONCTION : Vérification post-génération
# ============================================

def check_terraform_security(terraform_code: str, provider: str = None) -> dict:
    """
    Verifie le code Terraform contre les 6 politiques
    
    Args:
        terraform_code: Code Terraform à vérifier
        provider: Provider cloud (auto-détecté si None)
    
    Returns:
        dict: Rapport de sécurité avec violations, score, grade
    """
    if provider is None:
        provider = _detect_provider(terraform_code)
    
    logger.info(f"Vérification sécurité pour provider: {provider}")
    
    violations = []
    passed = []
    
    for policy_id, policy in SECURITY_POLICIES.items():
        if "check" in policy:
            try:
                # Passe le provider à la fonction de check
                check_result = policy["check"](terraform_code, provider)
                if check_result:
                    passed.append(policy_id)
                else:
                    violations.append({
                        "rule": policy_id,
                        "severity": policy["severity"],
                        "category": policy["category"],
                        "description": policy["description"]
                    })
            except Exception as e:
                logger.error(f"Erreur vérification {policy_id}: {e}")
                # En cas d'erreur, on considère comme violation pour sécurité
                violations.append({
                    "rule": policy_id,
                    "severity": "MEDIUM",
                    "category": policy.get("category", "Unknown"),
                    "description": f"Erreur lors de la vérification: {str(e)}"
                })
    
    if not violations:
        score = 100
    else:
        penalty_map = {"CRITICAL": 30, "HIGH": 20, "MEDIUM": 10}
        penalties = sum(penalty_map.get(v["severity"], 10) for v in violations)
        score = max(0, 100 - penalties)
    
    if score >= 90:
        grade, status = "A", "Excellent"
    elif score >= 75:
        grade, status = "B", "Bon"
    elif score >= 60:
        grade, status = "C", "Acceptable"
    else:
        grade, status = "D", "Insuffisant"
    
    return {
        "violations": violations,
        "passed_checks": passed,
        "total_issues": len(violations),
        "total_passed": len(passed),
        "security_score": score,
        "security_grade": grade,
        "security_status": status,
        "policies_checked": len(SECURITY_POLICIES)
    }
