import pytest
import requests_mock
from destination_mockapi.client import MockAPIClient

API_URL = "https://68cc13e1716562cf50764f2b.mockapi.io/api/v1"

class TestMockAPIClient:
    
    @pytest.fixture
    def client(self):
        return MockAPIClient(api_url=API_URL)
    
    @pytest.fixture
    def sample_user_data(self):
        return {
            "name": "John Doe",
            "avatar": "https://example.com/avatar.jpg"
        }
    
    @pytest.fixture
    def sample_users_response(self):
        return [
            {
                "createdAt": "2025-09-18T04:48:17.487Z",
                "name": "Stacy Bergnaum",
                "avatar": "https://cdn.jsdelivr.net/gh/faker-js/assets-person-portrait/female/512/80.jpg",
                "id": "1"
            },
            {
                "createdAt": "2025-09-18T05:22:11.123Z",
                "name": "John Doe",
                "avatar": "https://avatars.githubusercontent.com/u/12345678",
                "id": "2"
            }
        ]
    
    @pytest.fixture
    def sample_deals_response(self):
        return [
            {
                "createdAt": "2025-09-17T18:27:31.805Z",
                "name": "Jackie Glover",
                "avatar": "https://avatars.githubusercontent.com/u/90996305",
                "id": "1"
            },
            {
                "createdAt": "2025-09-18T09:53:43.574Z",
                "name": "Karen Smitham",
                "avatar": "https://avatars.githubusercontent.com/u/86362033",
                "id": "2"
            }
        ]
    
    def test_client_initialization(self, client):
        """Test client initializes correctly with config API URL"""
        assert client.api_url == API_URL
        assert client.timeout == 30
    
    def test_connection_success(self, client):
        """Test successful connection to MockAPI"""
        with requests_mock.Mocker() as m:
            m.get(f"{API_URL}/users", json=[])
            
            result = client.test_connection()
            assert result is True
    
    def test_connection_failure(self, client):
        """Test connection failure"""
        with requests_mock.Mocker() as m:
            m.get(f"{API_URL}/users", status_code=500)
            
            result = client.test_connection()
            assert result is False
    
    def test_get_users_success(self, client, sample_users_response):
        """Test successful retrieval of users"""
        with requests_mock.Mocker() as m:
            m.get(f"{API_URL}/users", json=sample_users_response)
            
            result = client.get_users(limit=10)
            assert len(result) == 2
            assert result[0]["name"] == "Stacy Bergnaum"
            assert result[1]["name"] == "John Doe"
            assert "createdAt" in result[0]
            assert "avatar" in result[0]
    
    def test_create_user_success(self, client, sample_user_data):
        """Test successful user creation"""
        created_user = {
            **sample_user_data, 
            "id": "123",
            "createdAt": "2025-09-18T12:00:00.000Z"
        }
        
        with requests_mock.Mocker() as m:
            m.post(f"{API_URL}/users", json=created_user)
            
            result = client.create_user(sample_user_data)
            assert result["id"] == "123"
            assert result["name"] == "John Doe"
            assert "createdAt" in result
    
    def test_create_deal_success(self, client):
        """Test successful deal creation"""
        deal_data = {
            "name": "Big Deal",
            "avatar": "https://example.com/deal.jpg"
        }
        created_deal = {
            **deal_data, 
            "id": "456",
            "createdAt": "2025-09-18T12:00:00.000Z"
        }
        
        with requests_mock.Mocker() as m:
            m.post(f"{API_URL}/deals", json=created_deal)
            
            result = client.create_deal(deal_data)
            assert result["id"] == "456"
            assert result["name"] == "Big Deal"
    
    def test_get_deals_success(self, client, sample_deals_response):
        """Test successful retrieval of deals"""
        with requests_mock.Mocker() as m:
            m.get(f"{API_URL}/deals", json=sample_deals_response)
            
            result = client.get_deals(limit=10)
            assert len(result) == 2
            assert result[0]["name"] == "Jackie Glover"
            assert result[1]["name"] == "Karen Smitham"