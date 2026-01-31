from .security_rules import get_secure_settings

# Configuration par provider
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


def generate_terraform_single_provider(provider_config: dict) -> str:
    """
    Genere le code Terraform pour un provider unique
    Extrait de l'ancienne fonction generate_terraform()
    """
    provider = provider_config.get("provider", "aws").lower()
    servers = provider_config.get("servers", 0)
    databases = provider_config.get("databases", 0)
    networks = provider_config.get("networks", 1)
    security_groups = provider_config.get("security_groups", 1)
    load_balancers = provider_config.get("load_balancers", 0)
    database_type = provider_config.get("database_type", "mysql").lower()
    
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
    
    # Load Balancers - Multi-cloud
    for i in range(load_balancers):
        if provider == "aws":
            code += f"""# Load Balancer {i+1} (AWS)
resource "aws_lb" "lb_{i+1}" {{
  name               = "lb-{i+1}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.sg_1.id]
  subnets            = [aws_subnet.private.id]
  
  enable_deletion_protection = false
  
  tags = {{
    Name        = "lb-{i+1}"
    Environment = "production"
  }}
}}

resource "aws_lb_target_group" "tg_{i+1}" {{
  name     = "tg-{i+1}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  
  health_check {{
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
    protocol            = "HTTP"
  }}
  
  tags = {{
    Name = "tg-{i+1}"
  }}
}}

resource "aws_lb_listener" "listener_{i+1}" {{
  load_balancer_arn = aws_lb.lb_{i+1}.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.ssl_certificate_arn
  
  default_action {{
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg_{i+1}.arn
  }}
}}

"""
        elif provider == "azure":
            code += f"""# Load Balancer {i+1} (Azure)
resource "azurerm_public_ip" "lb_ip_{i+1}" {{
  name                = "lb-ip-{i+1}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
  
  tags = {{
    Environment = "production"
  }}
}}

resource "azurerm_lb" "lb_{i+1}" {{
  name                = "lb-{i+1}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"
  
  frontend_ip_configuration {{
    name                 = "PublicIPAddress"
    public_ip_address_id = azurerm_public_ip.lb_ip_{i+1}.id
  }}
  
  tags = {{
    Environment = "production"
  }}
}}

resource "azurerm_lb_backend_address_pool" "backend_pool_{i+1}" {{
  name            = "BackEndAddressPool"
  loadbalancer_id = azurerm_lb.lb_{i+1}.id
}}

resource "azurerm_lb_probe" "probe_{i+1}" {{
  name            = "http-probe"
  loadbalancer_id = azurerm_lb.lb_{i+1}.id
  port            = 80
  protocol        = "Http"
  request_path    = "/"
}}

resource "azurerm_lb_rule" "rule_{i+1}" {{
  name                           = "LBRule"
  loadbalancer_id                = azurerm_lb.lb_{i+1}.id
  probe_id                       = azurerm_lb_probe.probe_{i+1}.id
  backend_address_pool_ids       = [azurerm_lb_backend_address_pool.backend_pool_{i+1}.id]
  frontend_ip_configuration_name = "PublicIPAddress"
  protocol                       = "Tcp"
  frontend_port                  = 443
  backend_port                   = 80
}}

"""
        elif provider == "gcp":
            code += f"""# Load Balancer {i+1} (GCP)
resource "google_compute_backend_service" "backend_{i+1}" {{
  name                  = "backend-{i+1}"
  protocol              = "HTTP"
  port_name             = "http"
  timeout_sec           = 30
  enable_cdn            = false
  load_balancing_scheme = "EXTERNAL"
  
  health_checks = [google_compute_health_check.health_check_{i+1}.id]
  
  backend {{
    group = google_compute_instance_group.instance_group_{i+1}.id
  }}
}}

resource "google_compute_health_check" "health_check_{i+1}" {{
  name               = "health-check-{i+1}"
  check_interval_sec = 10
  timeout_sec        = 5
  healthy_threshold = 2
  
  http_health_check {{
    port         = 80
    request_path = "/"
  }}
}}

resource "google_compute_instance_group" "instance_group_{i+1}" {{
  name        = "instance-group-{i+1}"
  description = "Instance group for load balancer"
  zone        = "{config["zone"]}"
  
  instances = [
    google_compute_instance.server_1.id
  ]
  
  named_port {{
    name = "http"
    port = 80
  }}
}}

resource "google_compute_url_map" "url_map_{i+1}" {{
  name            = "url-map-{i+1}"
  default_service = google_compute_backend_service.backend_{i+1}.id
}}

resource "google_compute_target_https_proxy" "https_proxy_{i+1}" {{
  name             = "https-proxy-{i+1}"
  url_map          = google_compute_url_map.url_map_{i+1}.id
  ssl_certificates = [var.gcp_ssl_certificate_id]
}}

resource "google_compute_global_forwarding_rule" "forwarding_rule_{i+1}" {{
  name       = "forwarding-rule-{i+1}"
  target     = google_compute_target_https_proxy.https_proxy_{i+1}.id
  port_range = "443"
}}

"""
    
    # Bases de donnees - Multi-cloud avec politiques de securite
    for i in range(databases):
        # Recupere les parametres securises
        secure_settings = get_secure_settings(provider)
        
        if provider == "aws":
            # Mapping des types de database vers engines AWS
            db_engines = {
                "mysql": ("mysql", "8.0"),
                "postgresql": ("postgres", "16.1"),
                "mariadb": ("mariadb", "10.11"),
                "mongodb": ("docdb", "5.0")  # DocumentDB pour MongoDB
            }
            
            engine, version = db_engines.get(database_type, ("mysql", "8.0"))
            
            code += f"""# Base de donnees {i+1} ({database_type.upper()}) - Politiques de securite appliquees
resource "aws_db_instance" "db_{i+1}" {{
  identifier        = "db-{i+1}"
  engine            = "{engine}"
  engine_version    = "{version}"
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
    DatabaseType = "{database_type}"
  }}
}}

"""
        elif provider == "azure":
            # Azure necessite des ressources differentes selon le type
            if database_type == "postgresql":
                code += f"""# PostgreSQL Server {i+1} - Politiques de securite appliquees
resource "azurerm_postgresql_server" "db_{i+1}" {{
  name                = "postgresql-{i+1}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  administrator_login          = "psqladmin"
  administrator_login_password = var.db_password
  
  sku_name   = "{config["db_sku"]}"
  storage_mb = 20480
  version    = "11"
  
  # Politiques de securite injectees automatiquement
  public_network_access_enabled    = {str(secure_settings.get("public_network_access_enabled", False)).lower()}
  ssl_enforcement_enabled          = {str(secure_settings.get("ssl_enforcement_enabled", True)).lower()}
  ssl_minimal_tls_version_enforced = "{secure_settings.get("ssl_minimal_tls_version_enforced", "TLS1_2")}"
  
  # Sauvegardes
  backup_retention_days = {secure_settings.get("backup_retention_days", 7)}
  
  tags = {{
    Environment = "production"
    DatabaseType = "postgresql"
  }}
}}

"""
            elif database_type == "mariadb":
                code += f"""# MariaDB Server {i+1} - Politiques de securite appliquees
resource "azurerm_mariadb_server" "db_{i+1}" {{
  name                = "mariadb-{i+1}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  administrator_login          = "mariadbadmin"
  administrator_login_password = var.db_password
  
  sku_name   = "{config["db_sku"]}"
  storage_mb = 20480
  version    = "10.3"
  
  # Politiques de securite injectees automatiquement
  public_network_access_enabled    = {str(secure_settings.get("public_network_access_enabled", False)).lower()}
  ssl_enforcement_enabled          = {str(secure_settings.get("ssl_enforcement_enabled", True)).lower()}
  ssl_minimal_tls_version_enforced = "{secure_settings.get("ssl_minimal_tls_version_enforced", "TLS1_2")}"
  
  # Sauvegardes
  backup_retention_days = {secure_settings.get("backup_retention_days", 7)}
  
  tags = {{
    Environment = "production"
    DatabaseType = "mariadb"
  }}
}}

"""
            else:  # mysql ou mongodb (Azure n'a pas MongoDB natif)
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
    DatabaseType = "{database_type}"
  }}
}}

"""
        elif provider == "gcp":
            # Mapping des types de database vers versions GCP
            gcp_db_versions = {
                "mysql": "MYSQL_8_0",
                "postgresql": "POSTGRES_16",
                "mariadb": "MYSQL_8_0",  # GCP n'a pas MariaDB natif, fallback MySQL
                "mongodb": "MYSQL_8_0"   # GCP n'a pas MongoDB natif, fallback MySQL
            }
            
            db_version = gcp_db_versions.get(database_type, "MYSQL_8_0")
            
            code += f"""# Cloud SQL {i+1} ({database_type.upper()}) - Politiques de securite appliquees
resource "google_sql_database_instance" "db_{i+1}" {{
  name             = "db-{i+1}"
  database_version = "{db_version}"
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
  
  labels = {{
    environment = "production"
    database_type = "{database_type}"
  }}
}}

"""
        elif provider == "openstack":
            code += f"""# Base de donnees {i+1} ({database_type.upper()}) - Politiques de securite appliquees
resource "openstack_db_instance_v1" "db_{i+1}" {{
  name      = "db-{i+1}"
  flavor_id = "{config["db_flavor"]}"
  size      = 20
  
  datastore {{
    type    = "{database_type}"
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
    
    # Variables pour load balancers
    if load_balancers > 0:
        if provider == "aws":
            code += """variable "ssl_certificate_arn" {
  description = "ARN du certificat SSL pour le load balancer"
  type        = string
}

"""
        elif provider == "gcp":
            code += """variable "gcp_ssl_certificate_id" {
  description = "ID du certificat SSL GCP"
  type        = string
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


def generate_terraform(infra: dict) -> str:
    """
    JSON infrastructure -> Code Terraform securise multi-cloud
    Supporte mono et multi-provider
    Format attendu: {"providers": [{"provider": "aws", "servers": 3, ...}]}
    """
    providers = infra.get("providers", [])
    
    # Si pas de providers, retourne vide
    if not providers:
        return "# Erreur: aucun provider specifie\n"
    
    # Cas mono-provider: genere directement
    if len(providers) == 1:
        return generate_terraform_single_provider(providers[0])
    
    # Cas multi-provider: concatene les codes Terraform
    terraform_code = "# Infrastructure Multi-Cloud\n"
    terraform_code += "# Genere automatiquement avec politiques de securite\n\n"
    terraform_code += "# ATTENTION: Ce fichier contient plusieurs providers\n"
    terraform_code += "# Il peut etre necessaire de le separer en plusieurs fichiers pour terraform apply\n\n"
    
    for idx, provider_config in enumerate(providers, 1):
        provider_name = provider_config.get("provider", "unknown").upper()
        terraform_code += f"\n{'#' * 80}\n"
        terraform_code += f"# SECTION {idx}: {provider_name}\n"
        terraform_code += f"{'#' * 80}\n\n"
        terraform_code += generate_terraform_single_provider(provider_config)
    
    return terraform_code