from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json
import os
from datetime import datetime
from security_rules import check_terraform_security, get_secure_settings

# Charger .env
load_dotenv()

# Initialiser Flask
app = Flask(__name__)
CORS(app)

# ============================================
# ÉTAPE 1 : EXPRESSION DES BESOINS
# Gemini comprend le langage naturel
# ============================================

# Config Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Clé GEMINI_API_KEY manquante dans .env")

client = genai.Client(api_key=GEMINI_API_KEY)

# Schéma JSON structuré (Modélisation)
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
            description="Nombre de bases de données (mets 0 si non mentionné explicitement)"
        ),
        "networks": types.Schema(
            type=types.Type.INTEGER,
            description="Nombre de réseaux"
        ),
        "load_balancers": types.Schema(
            type=types.Type.INTEGER,
            description="Nombre de load balancers (mets 0 si non mentionné explicitement)"
        ),
        "security_groups": types.Schema(
            type=types.Type.INTEGER,
            description="Nombre de groupes de sécurité"
        ),
    },
    required=["provider", "servers", "databases", "networks", "load_balancers", "security_groups"],
)

# ============================================
# ÉTAPE 2 : INTERFACE LOGICIELLE MULTI-CLOUD
# Support AWS, Azure, GCP, OpenStack
# ============================================

PROVIDER_CONFIGS = {
    "aws": {
        "region": "us-east-1",
        "instance_type": "t2.micro",
        "db_class": "db.t2.micro",
        "ami": "ami-0c55b159cbfafe1f0"
    },
    "azure": {
        "location": "East US",
        "vm_size": "Standard_B1s",
        "db_sku": "B_Gen5_1",
        "image_publisher": "Canonical",
        "image_offer": "UbuntuServer",
        "image_sku": "18.04-LTS"
    },
    "gcp": {
        "region": "us-central1",
        "zone": "us-central1-a",
        "machine_type": "f1-micro",
        "db_tier": "db-f1-micro",
        "image": "debian-cloud/debian-11"
    },
    "openstack": {
        "region": "RegionOne",
        "flavor": "m1.small",
        "db_flavor": "db.small",
        "image": "Ubuntu 20.04"
    }
}

# Les règles de sécurité sont dans security_rules.py
# Elles sont appliquées via check_terraform_security()

# ============================================
# MOTEUR DE CONVERSION (NLP/Visuel)
# ============================================

def extract_infrastructure_from_text_basic(description: str) -> dict:
    """Fallback : Analyse basique par mots-clés"""
    d = description.lower()
    
    # Détection provider
    provider = "aws"
    if "azure" in d:
        provider = "azure"
    elif "gcp" in d or "google" in d:
        provider = "gcp"
    elif "openstack" in d:
        provider = "openstack"
    
    # Détection composants
    import re
    numbers = re.findall(r'\d+', description)
    
    # Détection bases de données - Plus précise
    has_database = False
    db_keywords = ["database", "base de données", "bdd", "mysql", "postgresql", "postgres", "mariadb", "mongodb", "sql"]
    
    # Vérifier si un mot-clé DB est présent ET qu'on ne parle pas juste de serveur
    for keyword in db_keywords:
        if keyword in d:
            has_database = True
            break
    
    return {
        "provider": provider,
        "servers": int(numbers[0]) if numbers else 1,
        "databases": 1 if has_database else 0,
        "networks": 1,
        "load_balancers": 1 if "load balancer" in d or "loadbalancer" in d or "lb" in d else 0,
        "security_groups": 1,
    }

def detect_security_override_requests(description: str) -> list:
    """
    Détecte si l'utilisateur demande quelque chose qui viole les règles de sécurité
    
    Returns:
        list: Liste des demandes dangereuses détectées
    """
    warnings = []
    d = description.lower()
    
    # Détection : DB publique
    if any(keyword in d for keyword in ["publique", "public", "accessible internet", "accessible publiquement"]):
        if any(db in d for db in ["database", "db", "base", "mysql", "postgresql"]):
            warnings.append({
                "requested": "Base de données publique",
                "applied": "Base de données PRIVÉE (politique de sécurité)",
                "reason": "Les bases de données ne doivent jamais être accessibles depuis Internet",
                "alternative": "Utilisez un VPN, bastion host, ou connexion privée pour accéder à la base"
            })
    
    # Détection : Pas de chiffrement
    if any(keyword in d for keyword in ["sans chiffrement", "non chiffré", "unencrypted", "no encryption"]):
        warnings.append({
            "requested": "Données non chiffrées",
            "applied": "Chiffrement ACTIVÉ (politique de sécurité)",
            "reason": "Le chiffrement est obligatoire pour protéger les données sensibles",
            "alternative": "Le chiffrement est automatique et transparent"
        })
    
    # Détection : SSH ouvert à tous
    if any(keyword in d for keyword in ["ssh 0.0.0.0", "ssh public", "ssh ouvert"]):
        warnings.append({
            "requested": "SSH ouvert à tous",
            "applied": "SSH RESTREINT (politique de sécurité)",
            "reason": "SSH ne doit être accessible que depuis des IPs spécifiques",
            "alternative": "Configurez un VPN ou une whitelist d'IPs"
        })
    
    return warnings


def extract_infrastructure_with_gemini(description: str) -> dict:
    """Utilise Gemini pour comprendre la demande (NLP)"""
    try:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=json_schema,
            system_instruction=(
                "Tu es un architecte cloud expert. "
                "Analyse EXACTEMENT la demande utilisateur et génère UNIQUEMENT les composants explicitement demandés. "
                "\n\n"
                "RÈGLES STRICTES:\n"
                "- Si l'utilisateur ne mentionne PAS de base de données → databases: 0\n"
                "- Si l'utilisateur ne mentionne PAS de load balancer → load_balancers: 0\n"
                "- Ne JAMAIS rajouter de composants non demandés\n"
                "\n"
                "EXEMPLES:\n"
                "Demande: 'Je veux un serveur AWS' → {servers: 1, databases: 0, load_balancers: 0}\n"
                "Demande: 'Je veux 3 serveurs avec MySQL' → {servers: 3, databases: 1, load_balancers: 0}\n"
                "Demande: 'Une base de données' → {servers: 0, databases: 1, load_balancers: 0}\n"
                "\n"
                "Applique les meilleures pratiques de sécurité UNIQUEMENT sur ce qui est demandé."
            ),
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[description],
            config=config,
        )

        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            raise ValueError("Réponse Gemini vide")

        part = candidate.content.parts[0]

        if hasattr(part, "structured_data") and part.structured_data:
            return {"data": part.structured_data, "gemini_success": True}

        if hasattr(part, "text") and part.text:
            return {"data": json.loads(part.text), "gemini_success": True}

        raise ValueError("Réponse Gemini inexploitable")

    except Exception as e:
        print(f" Gemini fallback: {e}")
        fallback = extract_infrastructure_from_text_basic(description)
        return {"data": fallback, "gemini_success": False}

# ============================================
# ÉTAPE 3 : MOTEURS IA/IAC
# Génération Terraform + Ansible + Sécurité
# ============================================

def generate_terraform_code(infra: dict) -> str:
    """GÉNÉRATEUR TERRAFORM (IaC) - Multi-cloud avec recettes optimisées"""
    provider = infra.get("provider", "aws").lower()
    servers = infra.get("servers", 0)
    databases = infra.get("databases", 0)
    networks = infra.get("networks", 1)
    security_groups = infra.get("security_groups", 1)
    
    config = PROVIDER_CONFIGS.get(provider, PROVIDER_CONFIGS["aws"])
    
    # Header Terraform
    code = f"""# ============================================
# Infrastructure as Code (IaC) - {provider.upper()}
# Généré automatiquement avec recettes optimisées
# Conforme aux politiques de sécurité
# ============================================

terraform {{
  required_version = ">= 1.0"
  
  required_providers {{
"""
    
    # Provider specifique
    if provider == "aws":
        code += """    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
"""
    elif provider == "azure":
        code += """    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
"""
    elif provider == "gcp":
        code += """    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
"""
    elif provider == "openstack":
        code += """    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.0"
    }
"""
    
    code += """  }
}

"""
    
    # Configuration provider
    if provider == "aws":
        code += f"""provider "aws" {{
  region = "{config["region"]}"
}}

"""
    elif provider == "azure":
        code += f"""provider "azurerm" {{
  features {{}}
}}

"""
    elif provider == "gcp":
        code += f"""provider "google" {{
  project = var.gcp_project_id
  region  = "{config["region"]}"
}}

"""
    elif provider == "openstack":
        code += f"""provider "openstack" {{
  auth_url = var.openstack_auth_url
}}

"""
    
    # Réseau (Isolation réseau - Politique de sécurité)
    if networks > 0:
        if provider == "aws":
            code += """# Réseau privé isolé (Politique: network_isolation)
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name          = "main-vpc"
    Environment   = "production"
    SecurityLevel = "high"
  }
}

resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  
  tags = {
    Name          = "private-subnet"
    Environment   = "production"
    SecurityLevel = "high"
  }
}

"""
        elif provider == "azure":
            code += f"""# Groupe de ressources
resource "azurerm_resource_group" "main" {{
  name     = "rg-infrastructure"
  location = "{config["location"]}"
  
  tags = {{
    Environment   = "production"
    SecurityLevel = "high"
  }}
}}

# Réseau virtuel isolé
resource "azurerm_virtual_network" "main" {{
  name                = "vnet-main"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  tags = {{
    Environment   = "production"
    SecurityLevel = "high"
  }}
}}

resource "azurerm_subnet" "private" {{
  name                 = "subnet-private"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}}

"""
        elif provider == "gcp":
            code += f"""# Réseau VPC isolé
resource "google_compute_network" "main" {{
  name                    = "vpc-main"
  auto_create_subnetworks = false
}}

resource "google_compute_subnetwork" "private" {{
  name          = "subnet-private"
  ip_cidr_range = "10.0.1.0/24"
  region        = "{config["region"]}"
  network       = google_compute_network.main.id
}}

"""
        elif provider == "openstack":
            code += """# Réseau isolé
resource "openstack_networking_network_v2" "main" {
  name = "network-main"
}

resource "openstack_networking_subnet_v2" "private" {
  name       = "subnet-private"
  network_id = openstack_networking_network_v2.main.id
  cidr       = "10.0.1.0/24"
}

"""
    
    # Security Groups (Least Privilege)
    for i in range(security_groups):
        if provider == "aws":
            code += f"""# Security Group {i+1} (Least Privilege)
resource "aws_security_group" "sg_{i+1}" {{
  name        = "sg-{i+1}"
  description = "Security group avec principe du moindre privilège"
  vpc_id      = aws_vpc.main.id
  
  # HTTP/HTTPS uniquement
  ingress {{
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = {{
    Name          = "sg-{i+1}"
    Environment   = "production"
    SecurityLevel = "high"
  }}
}}

"""
    
    # Serveurs
    for i in range(servers):
        if provider == "aws":
            code += f"""# Serveur {i+1}
resource "aws_instance" "server_{i+1}" {{
  ami           = "{config["ami"]}"
  instance_type = "{config["instance_type"]}"
  subnet_id     = aws_subnet.private.id
  
  vpc_security_group_ids = [aws_security_group.sg_1.id]
  
  # Chiffrement du volume (encryption_at_rest)
  root_block_device {{
    encrypted = true
  }}
  
  # Monitoring activé
  monitoring = true
  
  tags = {{
    Name          = "server-{i+1}"
    Environment   = "production"
    SecurityLevel = "high"
  }}
}}

"""
        elif provider == "azure":
            code += f"""# VM {i+1} (Azure)
resource "azurerm_network_interface" "nic_{i+1}" {{
  name                = "nic-{i+1}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  ip_configuration {{
    name                          = "internal"
    subnet_id                     = azurerm_subnet.private.id
    private_ip_address_allocation = "Dynamic"
  }}
}}

resource "azurerm_linux_virtual_machine" "vm_{i+1}" {{
  name                = "vm-{i+1}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "{config["vm_size"]}"
  admin_username      = "adminuser"
  
  network_interface_ids = [azurerm_network_interface.nic_{i+1}.id]
  
  admin_ssh_key {{
    username   = "adminuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }}
  
  os_disk {{
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    # Chiffrement activé par défaut sur Azure
  }}
  
  source_image_reference {{
    publisher = "{config["image_publisher"]}"
    offer     = "{config["image_offer"]}"
    sku       = "{config["image_sku"]}"
    version   = "latest"
  }}
  
  tags = {{
    Environment   = "production"
    SecurityLevel = "high"
  }}
}}

"""
        elif provider == "gcp":
            code += f"""# Instance {i+1} (GCP)
resource "google_compute_instance" "server_{i+1}" {{
  name         = "server-{i+1}"
  machine_type = "{config["machine_type"]}"
  zone         = "{config["zone"]}"
  
  boot_disk {{
    initialize_params {{
      image = "{config["image"]}"
    }}
    # Chiffrement activé par défaut sur GCP
  }}
  
  network_interface {{
    subnetwork = google_compute_subnetwork.private.id
  }}
  
  labels = {{
    environment    = "production"
    security_level = "high"
  }}
}}

"""
    
    # Bases de données (No Public Access + Encryption)
    # Bases de données avec politiques de sécurité
    for i in range(databases):
        #  Récupérer les paramètres sécurisés depuis security_rules.py
        secure_settings = get_secure_settings("database", provider)
        
        if provider == "aws":
            code += f"""# Base de données {i+1} (Politiques de sécurité appliquées)
resource "aws_db_instance" "db_{i+1}" {{
  identifier        = "db-{i+1}"
  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = "{config["db_class"]}"
  allocated_storage = 20
  
  db_name  = "mydb"
  username = "admin"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.sg_1.id]
  
  #  Politiques de sécurité (depuis security_rules.py)
  publicly_accessible = {str(secure_settings.get("publicly_accessible", False)).lower()}
  storage_encrypted   = {str(secure_settings.get("storage_encrypted", True)).lower()}
  monitoring          = {str(secure_settings.get("monitoring", True)).lower()}
  
  # Logs CloudWatch
  enabled_cloudwatch_logs_exports = {secure_settings.get("enabled_cloudwatch_logs_exports", ["error", "general", "slowquery"])}
  
  # Sauvegardes
  backup_retention_period = {secure_settings.get("backup_retention_period", 7)}
  
  tags = {{
    Name          = "database-{i+1}"
    Environment   = "production"
    SecurityLevel = "high"
  }}
}}

"""
        elif provider == "azure":
            code += f"""# MySQL Server {i+1} (Politiques de sécurité appliquées)
resource "azurerm_mysql_server" "db_{i+1}" {{
  name                = "mysql-{i+1}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  administrator_login          = "mysqladmin"
  administrator_login_password = var.db_password
  
  sku_name   = "{config["db_sku"]}"
  storage_mb = 20480
  version    = "8.0"
  
  #  Politiques de sécurité (depuis security_rules.py)
  public_network_access_enabled = {str(secure_settings.get("public_network_access_enabled", False)).lower()}
  ssl_enforcement_enabled       = {str(secure_settings.get("ssl_enforcement_enabled", True)).lower()}
  ssl_minimal_tls_version_enforced = "{secure_settings.get("ssl_minimal_tls_version_enforced", "TLS1_2")}"
  
  # Sauvegardes
  backup_retention_days = {secure_settings.get("backup_retention_days", 7)}
  
  tags = {{
    Environment   = "production"
    SecurityLevel = "high"
  }}
}}

"""
        elif provider == "gcp":
            code += f"""# Cloud SQL {i+1} (Politiques de sécurité appliquées)
resource "google_sql_database_instance" "db_{i+1}" {{
  name             = "db-{i+1}"
  database_version = "MYSQL_8_0"
  region           = "{config["region"]}"
  
  settings {{
    tier = "{config["db_tier"]}"
    
    #  Politiques de sécurité (depuis security_rules.py)
    ip_configuration {{
      ipv4_enabled = {str(secure_settings.get("ipv4_enabled", False)).lower()}
      require_ssl  = {str(secure_settings.get("require_ssl", True)).lower()}
    }}
    
    insights_config {{
      query_insights_enabled = {str(secure_settings.get("query_insights_enabled", True)).lower()}
    }}
    
    backup_configuration {{
      enabled    = {str(secure_settings.get("backup_enabled", True)).lower()}
      start_time = "{secure_settings.get("backup_start_time", "03:00")}"
    }}
  }}
}}

"""
        elif provider == "openstack":
            code += f"""# Base de données {i+1} (Politiques de sécurité appliquées)
resource "openstack_db_instance_v1" "db_{i+1}" {{
  name      = "db-{i+1}"
  flavor_id = "{config["db_flavor"]}"
  size      = 20
  
  datastore {{
    type    = "mysql"
    version = "8.0"
  }}
  
  #  Politiques de sécurité (depuis security_rules.py)
  # OpenStack DB ne supporte pas tous les paramètres
  # Chiffrement géré au niveau volume
}}

"""
    
    # Variables sensibles (seulement si nécessaire)
    if databases > 0:
        code += """# Variables sensibles
variable "db_password" {
  description = "Mot de passe base de données"
  type        = string
  sensitive   = true
}

"""
    
    if provider == "gcp":
        code += """variable "gcp_project_id" {
  type = string
}

"""
    elif provider == "openstack":
        code += """variable "openstack_auth_url" {
  type = string
}

"""
    
    # Outputs
    code += """# Outputs
output "infrastructure_id" {
  value = "infra-${formatdate("YYYYMMDD-hhmm", timestamp())}"
}

"""
    
    return code

def generate_ansible_playbook(infra: dict) -> str:
    """GÉNÉRATEUR ANSIBLE (Configuration) - Déploiement automatisé"""
    provider = infra.get("provider", "aws")
    servers = infra.get("servers", 0)
    databases = infra.get("databases", 0)
    
    playbook = f"""---
# ============================================
# Ansible Playbook - Configuration automatisée
# Provider: {provider.upper()}
# Généré: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ============================================

- name: Configuration sécurisée de l'infrastructure
  hosts: all
  become: yes
  
  vars:
    environment: production
    provider: {provider}
    security_level: high
  
  tasks:
    - name: Mise à jour système
      apt:
        update_cache: yes
        upgrade: dist
      when: ansible_os_family == "Debian"
    
    - name: Installation paquets sécurité
      apt:
        name:
          - fail2ban
          - ufw
          - unattended-upgrades
        state: present
      when: ansible_os_family == "Debian"
    
    - name: Configuration firewall (Least Privilege)
      ufw:
        rule: allow
        port: "{{{{ item }}}}"
        proto: tcp
      loop:
        - 22
        - 443
      when: ansible_os_family == "Debian"
    
    - name: Blocage SSH par mot de passe
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PasswordAuthentication'
        line: 'PasswordAuthentication no'
      notify: Redémarrer SSH
  
  handlers:
    - name: Redémarrer SSH
      service:
        name: ssh
        state: restarted

"""
    
    if databases > 0:
        playbook += """
# Configuration base de données sécurisée
- name: Configuration MySQL sécurisée
  hosts: database_servers
  become: yes
  
  tasks:
    - name: Installation MySQL
      apt:
        name: mysql-server
        state: present
    
    - name: Configuration MySQL - Bind localhost uniquement
      lineinfile:
        path: /etc/mysql/mysql.conf.d/mysqld.cnf
        regexp: '^bind-address'
        line: 'bind-address = 127.0.0.1'
      notify: Redémarrer MySQL
    
    - name: Activation SSL MySQL
      lineinfile:
        path: /etc/mysql/mysql.conf.d/mysqld.cnf
        line: 'require_secure_transport = ON'
      notify: Redémarrer MySQL
  
  handlers:
    - name: Redémarrer MySQL
      service:
        name: mysql
        state: restarted

"""
    
    if servers > 0:
        playbook += """
# Configuration serveurs web
- name: Configuration Nginx sécurisé
  hosts: web_servers
  become: yes
  
  tasks:
    - name: Installation Nginx
      apt:
        name: nginx
        state: present
    
    - name: Configuration HTTPS uniquement
      template:
        src: nginx-ssl.conf.j2
        dest: /etc/nginx/sites-available/default
      notify: Recharger Nginx
    
    - name: Installation Certbot (Let's Encrypt)
      apt:
        name: certbot
        state: present
  
  handlers:
    - name: Recharger Nginx
      service:
        name: nginx
        state: reloaded

"""
    
    return playbook

# ============================================
# ROUTE API PRINCIPALE
# ============================================

@app.route("/generate", methods=["POST"])
def generate():
    """
    Terminal de commande unifié
    Génère Terraform + Ansible + Vérification sécurité
    """
    try:
        data = request.get_json(silent=True) or {}
        description = data.get("description", "").strip()
        if not description:
            return jsonify({"error": "Description manquante"}), 400

        #  ÉTAPE 0: Détecter les demandes dangereuses
        security_overrides = detect_security_override_requests(description)

        # ÉTAPE 1: Extraction des besoins (NLP)
        result = extract_infrastructure_with_gemini(description)
        infra_data = result["data"]
        gemini_success = result["gemini_success"]
        
        #  DEBUG: Logger l'infrastructure détectée
        print("=" * 60)
        print("🔍 DEBUG - Infrastructure détectée:")
        print(f"   Provider: {infra_data.get('provider')}")
        print(f"   Servers: {infra_data.get('servers')}")
        print(f"   Databases: {infra_data.get('databases')}")
        print(f"   Networks: {infra_data.get('networks')}")
        print(f"   Load Balancers: {infra_data.get('load_balancers')}")
        print(f"   Security Groups: {infra_data.get('security_groups')}")
        print(f"   Gemini success: {gemini_success}")
        print("=" * 60)

        # ÉTAPE 2: Génération IaC multi-cloud (Terraform)
        terraform_code = generate_terraform_code(infra_data)
        
        #  DEBUG: Compter les ressources réellement générées
        db_count_in_code = terraform_code.count('resource "aws_db_instance"') + \
                          terraform_code.count('resource "azurerm_mysql_server"') + \
                          terraform_code.count('resource "google_sql_database_instance"') + \
                          terraform_code.count('resource "openstack_db_instance_v1"')
        
        print(f"🔍 DEBUG - Bases de données dans le code Terraform: {db_count_in_code}")
        
        if db_count_in_code != infra_data.get('databases', 0):
            print(f"  INCOHÉRENCE DÉTECTÉE !")
            print(f"   Demandé: {infra_data.get('databases', 0)} DB")
            print(f"   Généré: {db_count_in_code} DB")

        
        # ÉTAPE 3: Génération Configuration (Ansible)
        ansible_playbook = generate_ansible_playbook(infra_data)
        
        # ÉTAPE 4: Vérification sécurité (Bibliothèque de politiques)
        security_report = check_terraform_security(terraform_code)
        
        #  Ajouter les avertissements de sécurité
        if security_overrides:
            security_report["security_overrides"] = security_overrides

        # Message personnalisé
        message = f"Infrastructure {infra_data.get('provider', 'aws').upper()} générée avec succès !"
        if not gemini_success:
            message += " (mode fallback)"
        if security_overrides:
            message += f"  {len(security_overrides)} demande(s) dangereuse(s) bloquée(s)"

        # Réponse unifiée
        response = {
            "success": True,
            "message": message,
            "infrastructure": {
                "provider": infra_data.get("provider", "aws"),
                "servers": infra_data.get("servers", 0),
                "databases": infra_data.get("databases", 0),
                "networks": infra_data.get("networks", 0),
                "load_balancers": infra_data.get("load_balancers", 0),
                "security_groups": infra_data.get("security_groups", 0),
            },
            "terraform_code": terraform_code,
            "ansible_playbook": ansible_playbook,
            "security_report": security_report,
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "supported_providers": list(PROVIDER_CONFIGS.keys())
    })

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" TERMINAL DE COMMANDE UNIFIÉ - Multi-Cloud IaC")
    print("="*60)
    print(f"Providers supportés: {', '.join(PROVIDER_CONFIGS.keys()).upper()}")
    print(f" Vérification sécurité: security_rules.py")
    print(f" Moteurs: Terraform + Ansible")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
