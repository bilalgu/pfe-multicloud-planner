"""
Tests unitaires pour le module NLP
"""
import pytest
import os
from modules.nlp import extract_infrastructure, InfrastructureSchema, mock_extract_infrastructure


class TestNLP:
    """Tests pour l'extraction d'infrastructure"""
    
    def test_mock_extract_aws_server(self):
        """Test extraction mock d'un serveur AWS"""
        os.environ["AI_MODE"] = "mock"
        result = extract_infrastructure("Je veux un serveur AWS")
        assert result["provider"] == "aws"
        assert result["servers"] >= 1
        assert result["networks"] >= 1
    
    def test_mock_extract_gcp_with_db(self):
        """Test extraction mock GCP avec base de données"""
        os.environ["AI_MODE"] = "mock"
        result = extract_infrastructure("Je veux 2 serveurs GCP avec MySQL")
        assert result["provider"] == "gcp"
        assert result["servers"] == 2
        assert result["databases"] == 1
    
    def test_mock_extract_azure(self):
        """Test extraction mock Azure"""
        os.environ["AI_MODE"] = "mock"
        result = extract_infrastructure("Serveur Azure")
        assert result["provider"] == "azure"
        assert result["servers"] >= 1
    
    def test_infrastructure_schema_validation(self):
        """Test validation du schéma Pydantic"""
        valid_data = {
            "provider": "aws",
            "servers": 2,
            "databases": 1,
            "networks": 1,
            "load_balancers": 0,
            "security_groups": 1
        }
        schema = InfrastructureSchema(**valid_data)
        assert schema.provider == "aws"
        assert schema.servers == 2
    
    def test_infrastructure_schema_invalid_provider(self):
        """Test validation avec provider invalide"""
        data = {
            "provider": "invalid",
            "servers": 1,
            "databases": 0,
            "networks": 1,
            "load_balancers": 0,
            "security_groups": 1
        }
        schema = InfrastructureSchema(**data)
        # Doit convertir en 'aws' par défaut
        assert schema.provider == "aws"
    
    def test_infrastructure_schema_negative_values(self):
        """Test validation avec valeurs négatives"""
        data = {
            "provider": "aws",
            "servers": -1,  # Invalide
            "databases": 0,
            "networks": 1,
            "load_balancers": 0,
            "security_groups": 1
        }
        with pytest.raises(Exception):  # Pydantic devrait lever une erreur
            InfrastructureSchema(**data)
