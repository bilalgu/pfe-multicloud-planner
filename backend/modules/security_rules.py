"""
BIBLIOTHÈQUE DE GÉNÉRATION DE POLITIQUES DE SÉCURITÉ
6 règles essentielles pour le MVP
"""

import re

# ============================================
# POLITIQUES DE SÉCURITÉ (6 règles MVP)
# ============================================

SECURITY_POLICIES = {
    "db_no_public_ip": {
        "name": "Base de données privée",
        "description": "Les bases de données ne doivent jamais être accessibles depuis Internet",
        "severity": "HIGH",
        "category": "Network Access",
        "terraform_settings": {
            "aws": {"publicly_accessible": False},
            "azure": {"public_network_access_enabled": False},
            "gcp": {"ipv4_enabled": False},
            "openstack": {"public": False}
        },
        "check": lambda code: "publicly_accessible = true" not in code.lower()
    },
    
    "encryption_at_rest": {
        "name": "Chiffrement au repos",
        "description": "Toutes les données doivent être chiffrées au repos",
        "severity": "HIGH",
        "category": "Encryption",
        "terraform_settings": {
            "aws": {"storage_encrypted": True, "encrypted": True},
            "azure": {"infrastructure_encryption_enabled": True},
            "gcp": {"disk_encryption_key": "customer-managed"},
            "openstack": {"encrypted": True}
        },
        "check": lambda code: "encrypted" in code.lower() or "encryption" in code.lower()
    },
    
    "ssl_required": {
        "name": "SSL/TLS obligatoire",
        "description": "Toutes les connexions doivent utiliser SSL/TLS",
        "severity": "HIGH",
        "category": "Encryption",
        "terraform_settings": {
            "aws": {"require_ssl": True},
            "azure": {"ssl_enforcement_enabled": True, "ssl_minimal_tls_version_enforced": "TLS1_2"},
            "gcp": {"require_ssl": True},
            "openstack": {"ssl_required": True}
        },
        "check": lambda code: "ssl" in code.lower() or "tls" in code.lower()
    },
    
    "monitoring_enabled": {
        "name": "Surveillance active",
        "description": "La surveillance et les logs doivent être activés",
        "severity": "MEDIUM",
        "category": "Monitoring",
        "terraform_settings": {
            "aws": {"monitoring": True, "enabled_cloudwatch_logs_exports": ["error", "general", "slowquery"]},
            "azure": {"insights_enabled": True},
            "gcp": {"query_insights_enabled": True},
            "openstack": {"logging_enabled": True}
        },
        "check": lambda code: "monitoring" in code.lower() or "logs" in code.lower()
    },
    
    "backup_enabled": {
        "name": "Sauvegardes automatiques",
        "description": "Les sauvegardes doivent être configurées",
        "severity": "MEDIUM",
        "category": "Backup & Recovery",
        "terraform_settings": {
            "aws": {"backup_retention_period": 7},
            "azure": {"backup_retention_days": 7},
            "gcp": {"backup_enabled": True, "backup_start_time": "03:00"},
            "openstack": {"backup_enabled": True}
        },
        "check": lambda code: "backup" in code.lower()
    },
    
    "no_hardcoded_credentials": {
        "name": "Pas de credentials en dur",
        "description": "Les mots de passe ne doivent jamais être hardcodés",
        "severity": "CRITICAL",
        "category": "Identity & Access",
        "terraform_settings": {
            "description": "Utiliser des variables sensibles"
        },
        "check": lambda code: not any(
            pattern in code
            for pattern in ['password = "', 'secret = "', 'api_key = "']
        )
    }
}

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
