import sys, json
import os
import tempfile

def generate_terraform_code(infrastructure_json):
    """
    Génère le code Terraform à partir du JSON
    """
    provider = infrastructure_json.get("provider", "aws")
    region = infrastructure_json.get("region", "eu-west-1")
    resources = infrastructure_json.get("resources", {})
    networks = infrastructure_json.get("networks", 1)
    security_groups = infrastructure_json.get("security_groups", 1)
    compute = resources.get("compute", 0)
    database = resources.get("database", {})


    terraform_code = f'''# Infrastructure générée automatiquement
# Provider: {provider.upper()}

terraform {{
  required_version = ">= 1.0"
  
  required_providers {{
    {provider} = {{
      source  = "hashicorp/{provider}"
      version = "~> 5.0"
    }}
  }}
}}

provider "{provider}" {{
  region = "{region}"
  # Configurez vos credentials ici
}}

'''
    
    # Génération des réseaux
    if networks > 0:
        terraform_code += f'''# Réseau VPC
resource "{provider}_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {{
    Name        = "main-vpc"
    Environment = "production"
    SecurityLevel = "high"
  }}
}}

# Subnet public
resource "{provider}_subnet" "public" {{
  vpc_id                  = {provider}_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  
  tags = {{
    Name        = "public-subnet"
    Environment = "production"
    SecurityLevel = "high"
  }}
}}

'''

    # Génération des groupes de sécurité
    for i in range(security_groups):
        terraform_code += f'''# Groupe de sécurité {i+1}
resource "{provider}_security_group" "main_{i+1}" {{
  name        = "main-sg-{i+1}"
  description = "Groupe de sécurité principal {i+1}"
  vpc_id      = {provider}_vpc.main.id
  
  ingress {{
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
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
    Name        = "main-sg-{i+1}"
    Environment = "production"
    SecurityLevel = "high"
  }}
}}

'''

    # Génération des serveurs
    for i in range(compute):
        terraform_code += f'''# Serveur {i+1}
resource "{provider}_instance" "server_{i+1}" {{
  ami           = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2
  instance_type = "t2.micro"
  subnet_id     = {provider}_subnet.public.id
  
  vpc_security_group_ids = [{provider}_security_group.main_1.id]
  
  tags = {{
    Name        = "server-{i+1}"
    Environment = "production"
    SecurityLevel = "high"
  }}
}}

'''

    # Génération des bases de données
    if database :
        terraform_code += f'''# Base de données
resource "{provider}_db_instance" "database" {{
  identifier     = "db-main"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t2.micro"
  allocated_storage = 20
  storage_type   = "gp2"
  
  db_name  = "mydb"
  username = "admin"
  password = "ChangeMe123!"  # À changer en production
  
  vpc_security_group_ids = [{provider}_security_group.main_1.id]

  publicly_accessible = {str(database.get("publicly_accessible", False)).lower()}
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"
  
  tags = {{
    Name        = "database-{i+1}"
    Environment = "production"
    SecurityLevel = "high"
  }}
}}

'''
        
    # Outputs
    terraform_code += '''# Outputs
output "vpc_id" {
  value = ''' + f'{provider}_vpc.main.id' + '''
}

output "public_subnet_id" {
  value = ''' + f'{provider}_subnet.public.id' + '''
}
'''

    return terraform_code

# Transformation du Json en argument en fichier terraform

# Vérife l'argument
if len(sys.argv) < 2:
    print("Erreur: JSON manquant en argument")
    exit(1)

json_path = sys.argv[1]

# Ouvre le fichier Json
with open(json_path) as f:
    data = json.load(f)

tf_code = generate_terraform_code(data)

# Destination provisoire
tmp_dir = tempfile.gettempdir()
output_path = os.path.join(tmp_dir, "main.tf")
with open(output_path, "w") as f:
    f.write(tf_code)

print(f"Terraform généré dans {output_path}")
