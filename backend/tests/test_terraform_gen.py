"""
Tests unitaires pour le module Terraform Generation
"""
import pytest
from modules.terraform_gen import generate_terraform

class TestTerraformGen:
    """Tests pour la génération Terraform"""
    
    def test_generate_aws_simple(self):
        """Test génération AWS simple"""
        # Nouveau format avec liste de providers
        infra = {
            "providers": [
                {
                    "provider": "aws",
                    "servers": 1,
                    "databases": 0,
                    "networks": 1,
                    "load_balancers": 0,
                    "security_groups": 1
                }
            ]
        }
        code = generate_terraform(infra)
        assert "provider \"aws\"" in code
        assert "aws_instance" in code
        assert "aws_vpc" in code
    
    def test_generate_aws_with_db(self):
        """Test génération AWS avec base de données"""
        # Nouveau format avec liste de providers
        infra = {
            "providers": [
                {
                    "provider": "aws",
                    "servers": 2,
                    "databases": 1,
                    "networks": 1,
                    "load_balancers": 0,
                    "security_groups": 1
                }
            ]
        }
        code = generate_terraform(infra)
        assert "aws_db_instance" in code
        assert "var.db_password" in code
    
    def test_generate_aws_with_lb(self):
        """Test génération AWS avec load balancer"""
        # Nouveau format avec liste de providers
        infra = {
            "providers": [
                {
                    "provider": "aws",
                    "servers": 2,
                    "databases": 0,
                    "networks": 1,
                    "load_balancers": 1,
                    "security_groups": 1
                }
            ]
        }
        code = generate_terraform(infra)
        assert "aws_lb" in code
        assert "aws_lb_target_group" in code
    
    def test_generate_gcp(self):
        """Test génération GCP"""
        # Nouveau format avec liste de providers
        infra = {
            "providers": [
                {
                    "provider": "gcp",
                    "servers": 1,
                    "databases": 0,
                    "networks": 1,
                    "load_balancers": 0,
                    "security_groups": 1
                }
            ]
        }
        code = generate_terraform(infra)
        assert "provider \"google\"" in code
        assert "google_compute_instance" in code
    
    def test_generate_azure(self):
        """Test génération Azure"""
        # Nouveau format avec liste de providers
        infra = {
            "providers": [
                {
                    "provider": "azure",
                    "servers": 1,
                    "databases": 0,
                    "networks": 1,
                    "load_balancers": 0,
                    "security_groups": 1
                }
            ]
        }
        code = generate_terraform(infra)
        assert "provider \"azurerm\"" in code
        assert "azurerm_linux_virtual_machine" in code