"""
Tests unitaires pour le module NLP
"""
import pytest
import os
from modules.nlp import extract_infrastructure, InfrastructureSchema, ProviderConfig, mock_extract_infrastructure

class TestNLP:
    """Tests pour l'extraction d'infrastructure"""
    
    def test_mock_extract_aws_server(self):
        """Test extraction mock d'un serveur AWS"""
        os.environ["AI_MODE"] = "mock"
        result = extract_infrastructure("Je veux un serveur AWS")
        # Nouveau format avec liste de providers
        assert "providers" in result
        assert len(result["providers"]) >= 1
        assert result["providers"][0]["provider"] == "aws"
        assert result["providers"][0]["servers"] >= 1
        assert result["providers"][0]["networks"] >= 1
    
    def test_mock_extract_gcp_with_db(self):
        """Test extraction mock GCP avec base de données"""
        os.environ["AI_MODE"] = "mock"
        result = extract_infrastructure("Je veux 2 serveurs GCP avec MySQL")
        # Nouveau format avec liste de providers
        assert "providers" in result
        assert len(result["providers"]) >= 1
        assert result["providers"][0]["provider"] == "gcp"
        assert result["providers"][0]["servers"] == 2
        assert result["providers"][0]["databases"] == 1
    
    def test_mock_extract_azure(self):
        """Test extraction mock Azure"""
        os.environ["AI_MODE"] = "mock"
        result = extract_infrastructure("Serveur Azure")
        # Nouveau format avec liste de providers
        assert "providers" in result
        assert len(result["providers"]) >= 1
        assert result["providers"][0]["provider"] == "azure"
        assert result["providers"][0]["servers"] >= 1
    
    def test_infrastructure_schema_validation(self):
        """Test validation du schéma Pydantic"""
        # Nouveau format avec liste de providers
        valid_data = {
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
        schema = InfrastructureSchema(**valid_data)
        assert schema.providers[0].provider == "aws"
        assert schema.providers[0].servers == 2
    
    def test_infrastructure_schema_invalid_provider(self):
        """Test validation avec provider invalide"""
        # Nouveau format avec liste de providers
        data = {
            "providers": [
                {
                    "provider": "invalid",
                    "servers": 1,
                    "databases": 0,
                    "networks": 1,
                    "load_balancers": 0,
                    "security_groups": 1
                }
            ]
        }
        schema = InfrastructureSchema(**data)
        # Doit convertir en 'aws' par défaut
        assert schema.providers[0].provider == "aws"
    
    def test_infrastructure_schema_negative_values(self):
        """Test validation avec valeurs négatives"""
        # Nouveau format avec liste de providers
        data = {
            "providers": [
                {
                    "provider": "aws",
                    "servers": -1,  # Invalide
                    "databases": 0,
                    "networks": 1,
                    "load_balancers": 0,
                    "security_groups": 1
                }
            ]
        }
        with pytest.raises(Exception):  # Pydantic devrait lever une erreur
            InfrastructureSchema(**data)