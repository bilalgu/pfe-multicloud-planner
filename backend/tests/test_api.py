"""
Tests d'intégration pour l'API Flask
"""
import pytest
import os
from app import app


@pytest.fixture
def client():
    """Client de test Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPI:
    """Tests pour l'API Flask"""
    
    def test_health_endpoint(self, client):
        """Test endpoint health"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
    
    def test_generate_empty_description(self, client):
        """Test génération avec description vide"""
        os.environ["AI_MODE"] = "mock"
        response = client.post('/generate', 
                              json={"description": ""})
        assert response.status_code == 400
    
    def test_generate_missing_description(self, client):
        """Test génération sans description"""
        os.environ["AI_MODE"] = "mock"
        response = client.post('/generate', 
                              json={})
        assert response.status_code == 400
    
    def test_generate_invalid_json(self, client):
        """Test génération avec JSON invalide"""
        response = client.post('/generate',
                              data="invalid json",
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_generate_success_mock(self, client):
        """Test génération réussie en mode mock"""
        os.environ["AI_MODE"] = "mock"
        response = client.post('/generate',
                              json={"description": "Je veux un serveur AWS"})
        assert response.status_code == 200
        data = response.get_json()
        assert "json" in data
        assert "security" in data
        assert "terraform" in data
    
    def test_history_endpoint(self, client):
        """Test endpoint history"""
        response = client.get('/api/history')
        assert response.status_code == 200
        data = response.get_json()
        assert "runs" in data
        assert "total" in data
