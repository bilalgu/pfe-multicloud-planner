"""
Tests unitaires pour le module Security
"""
import pytest
from modules.security import detect_dangerous_requests, validate_infrastructure
from modules.security_rules import check_terraform_security


class TestSecurity:
    """Tests pour la validation de sécurité"""
    
    def test_detect_public_database(self):
        """Test détection base de données publique"""
        warnings = detect_dangerous_requests("Je veux une base de données publique")
        assert len(warnings) > 0
        assert any("publique" in w["requested"].lower() for w in warnings)
    
    def test_detect_no_encryption(self):
        """Test détection sans chiffrement"""
        warnings = detect_dangerous_requests("Base de données sans chiffrement")
        assert len(warnings) > 0
    
    def test_detect_ssh_open(self):
        """Test détection SSH ouvert"""
        warnings = detect_dangerous_requests("Serveur avec SSH ouvert au public")
        assert len(warnings) > 0
    
    def test_safe_request(self):
        """Test requête sécurisée"""
        warnings = detect_dangerous_requests("Je veux un serveur AWS privé")
        assert len(warnings) == 0
    
    def test_check_terraform_security_aws(self):
        """Test vérification sécurité Terraform AWS"""
        terraform_code = """
        provider "aws" {
          region = "us-east-1"
        }
        
        resource "aws_instance" "server" {
          encrypted = true
          monitoring = true
        }
        """
        report = check_terraform_security(terraform_code, "aws")
        assert "security_score" in report
        assert report["security_score"] >= 0
    
    def test_check_terraform_security_azure(self):
        """Test vérification sécurité Terraform Azure"""
        terraform_code = """
        provider "azurerm" {
          features {}
        }
        
        resource "azurerm_linux_virtual_machine" "vm" {
          # Azure chiffre par défaut
        }
        """
        report = check_terraform_security(terraform_code, "azure")
        assert "security_score" in report
