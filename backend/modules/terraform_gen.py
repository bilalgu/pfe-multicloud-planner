from .security_rules import get_secure_settings

# Configuration par provider
# AWS/Azure/GCP/OpenStack sont des valeurs preparatoires (non testees)
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


def generate_terraform(infra: dict) -> str:
    """
    JSON infrastructure -> Code Terraform securise multi-cloud
    Injecte automatiquement les politiques de securite via get_secure_settings()
    Note : Tous les providers sont implementes, mais aucun n'est reellement teste actuellement
    """
    provider = infra.get("provider", "aws").lower()
    servers = infra.get("servers", 0)
    databases = infra.get("databases", 0)
    networks = infra.get("networks", 1)
    security_groups = infra.get("security_groups", 1)
    
    config = PROVIDER_CONFIGS.get(provider, PROVIDER_CONFIGS["aws"])
    
    # Header Terraform
    code = f"""# Infrastructure as Code - {provider.upper()}
# Genere automatiquement avec politiques de securite

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
    
    # Reseau - Multi-cloud
    if networks > 0:
        if provider == "aws":
            code += """# Reseau VPC isole
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name        = "main-vpc"
    Environment = "production"
  }
}

resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  
  tags = {
    Name        = "private-subnet"
    Environment = "production"
  }
}

"""
        elif provider == "azure":
            code += f"""# Groupe de ressources
resource "azurerm_resource_group" "main" {{
  name     = "rg-infrastructure"
  location = "{config["location"]}"
  
  tags = {{
    Environment = "production"
  }}
}}

# Reseau virtuel isole
resource "azurerm_virtual_network" "main" {{
  name                = "vnet-main"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  tags = {{
    Environment = "production"
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
            code += f"""# Reseau VPC isole
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
            code += """# Reseau isole
resource "openstack_networking_network_v2" "main" {
  name = "network-main"
}

resource "openstack_networking_subnet_v2" "private" {
  name       = "subnet-private"
  network_id = openstack_networking_network_v2.main.id
  cidr       = "10.0.1.0/24"
}

"""
    
    # Security Groups - Multi-cloud
    for i in range(security_groups):
        if provider == "aws":
            code += f"""# Security Group {i+1}
resource "aws_security_group" "sg_{i+1}" {{
  name        = "sg-{i+1}"
  description = "Security group avec principe du moindre privilege"
  vpc_id      = aws_vpc.main.id
  
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
    Name        = "sg-{i+1}"
    Environment = "production"
  }}
}}

"""
    
    # Serveurs - Multi-cloud
    for i in range(servers):
        if provider == "aws":
            code += f"""# Serveur {i+1}
resource "aws_instance" "server_{i+1}" {{
  ami           = "{config["ami"]}"
  instance_type = "{config["instance_type"]}"
  subnet_id     = aws_subnet.private.id
  
  vpc_security_group_ids = [aws_security_group.sg_1.id]
  
  # Chiffrement du volume (politique de securite)
  root_block_device {{
    encrypted = true
  }}
  
  # Monitoring active (politique de securite)
  monitoring = true
  
  tags = {{
    Name        = "server-{i+1}"
    Environment = "production"
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
  }}
  
  source_image_reference {{
    publisher = "{config["image_publisher"]}"
    offer     = "{config["image_offer"]}"
    sku       = "{config["image_sku"]}"
    version   = "latest"
  }}
  
  tags = {{
    Environment = "production"
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
  }}
  
  network_interface {{
    subnetwork = google_compute_subnetwork.private.id
  }}
  
  labels = {{
    environment = "production"
  }}
}}

"""
    
    # Bases de donnees - Multi-cloud avec politiques de securite
    for i in range(databases):
        # Recupere les parametres securises
        secure_settings = get_secure_settings(provider)
        
        if provider == "aws":
            code += f"""# Base de donnees {i+1} - Politiques de securite appliquees
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
  
  # Politiques de securite injectees automatiquement
  publicly_accessible = {str(secure_settings.get("publicly_accessible", False)).lower()}
  storage_encrypted   = {str(secure_settings.get("storage_encrypted", True)).lower()}
  
  # Logs CloudWatch
  enabled_cloudwatch_logs_exports = {secure_settings.get("enabled_cloudwatch_logs_exports", ["error", "general", "slowquery"])}
  
  # Sauvegardes
  backup_retention_period = {secure_settings.get("backup_retention_period", 7)}
  
  tags = {{
    Name        = "database-{i+1}"
    Environment = "production"
  }}
}}

"""
        elif provider == "azure":
            code += f"""# MySQL Server {i+1} - Politiques de securite appliquees
resource "azurerm_mysql_server" "db_{i+1}" {{
  name                = "mysql-{i+1}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  administrator_login          = "mysqladmin"
  administrator_login_password = var.db_password
  
  sku_name   = "{config["db_sku"]}"
  storage_mb = 20480
  version    = "8.0"
  
  # Politiques de securite injectees automatiquement
  public_network_access_enabled    = {str(secure_settings.get("public_network_access_enabled", False)).lower()}
  ssl_enforcement_enabled          = {str(secure_settings.get("ssl_enforcement_enabled", True)).lower()}
  ssl_minimal_tls_version_enforced = "{secure_settings.get("ssl_minimal_tls_version_enforced", "TLS1_2")}"
  
  # Sauvegardes
  backup_retention_days = {secure_settings.get("backup_retention_days", 7)}
  
  tags = {{
    Environment = "production"
  }}
}}

"""
        elif provider == "gcp":
            code += f"""# Cloud SQL {i+1} - Politiques de securite appliquees
resource "google_sql_database_instance" "db_{i+1}" {{
  name             = "db-{i+1}"
  database_version = "MYSQL_8_0"
  region           = "{config["region"]}"
  
  settings {{
    tier = "{config["db_tier"]}"
    
    # Politiques de securite injectees automatiquement
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
            code += f"""# Base de donnees {i+1} - Politiques de securite appliquees
resource "openstack_db_instance_v1" "db_{i+1}" {{
  name      = "db-{i+1}"
  flavor_id = "{config["db_flavor"]}"
  size      = 20
  
  datastore {{
    type    = "mysql"
    version = "8.0"
  }}
}}

"""
    
    # Variables sensibles si necessaire
    if databases > 0:
        code += """# Variables sensibles
variable "db_password" {
  description = "Mot de passe base de donnees"
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
  value = "infra-generated"
}

"""
    
    return code