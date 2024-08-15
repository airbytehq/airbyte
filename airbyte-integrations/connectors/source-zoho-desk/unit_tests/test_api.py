# test_zoho_api.py

import pytest
from unittest.mock import Mock
import json
from source_zoho_desk.api import ZohoAPI

@pytest.fixture
def config():
    return {
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
        "dc_region": "US",
        "environment": "Developer",
        "edition": "Free",
    }

def test_cached_authenticator(config):
    api = ZohoAPI(config)
    assert api.authenticator is api.authenticator

@pytest.mark.parametrize(
    ("region", "environment", "expected_result"),
    (
        ("US", "Developer", "https://developer.desk.zoho.com"),
        ("US", "Production", "https://desk.zoho.com"),
        ("US", "Sandbox", "https://sandbox.desk.zoho.com"),
        ("AU", "Developer", "https://developer.desk.zoho.com.au"),
        ("IN", "Production", "https://desk.zoho.in"),
        ("CN", "Sandbox", "https://sandbox.desk.zoho.com.cn"),
    ),
)
def test_api_url(config, region, environment, expected_result):
    config["dc_region"] = region
    config["environment"] = environment
    api = ZohoAPI(config)
    assert api.api_url == expected_result

def mock_request(mocker, request):
    mocker.patch("source_zoho_desk.api.requests.get", request)
    mocker.patch("source_zoho_desk.api.ZohoOauth2Authenticator.get_auth_header", Mock(return_value={}))

def test_check_connection_success(mocker, config):
    mock_request(mocker, Mock(return_value=Mock(status_code=200, content=b'{"access_token": "token", "expires_in": 3600}')))
    api = ZohoAPI(config)
    assert api.check_connection() == (True, None)

def test_check_connection_fail(mocker, config):
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.content = b"Authentication failure"
    
    mocker.patch("source_zoho_desk.api.requests.get", return_value=mock_response)
    mocker.patch("source_zoho_desk.api.ZohoOauth2Authenticator.get_auth_header", Mock(return_value={}))
    
    api = ZohoAPI(config)
    assert api.check_connection() == (False, b"Authentication failure")

def test_json_from_path_success(mocker, config):
    mock_response = {
        "data": {
            "modules": ["mocked_module1", "mocked_module2"]
        }
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json = Mock(return_value=mock_response)
    
    mocker.patch("source_zoho_desk.api.requests.get", return_value=mock_response_obj)
    mocker.patch("source_zoho_desk.api.ZohoOauth2Authenticator.get_auth_header", Mock(return_value={}))
    
    api = ZohoAPI(config)
    response = api._json_from_path("/api/v1/organizationFields", "modules")
    assert response == mock_response['data']

def test_json_from_path_fail(mocker, config):
    mock_request(mocker, Mock(return_value=Mock(status_code=204, content=b"No content")))
    api = ZohoAPI(config)
    assert api._json_from_path("/fields", "fields") == []

def test_module_settings(mocker, config):
    mock_response = {
        "data": [
            {"id": 1, "name": "module1"},
            {"id": 2, "name": "module2"}
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json = Mock(return_value=mock_response)
    
    mocker.patch("source_zoho_desk.api.requests.get", return_value=mock_response_obj)
    mocker.patch("source_zoho_desk.api.ZohoOauth2Authenticator.get_auth_header", Mock(return_value={}))
    
    api = ZohoAPI(config)
    response = api.module_settings("module_name")
    assert response == mock_response['data']

def test_modules_settings(mocker, config):
    mock_response = {
        "data": [
            {"id": 1, "name": "module1"},
            {"id": 2, "name": "module2"}
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json = Mock(return_value=mock_response)
    
    mocker.patch("source_zoho_desk.api.requests.get", return_value=mock_response_obj)
    mocker.patch("source_zoho_desk.api.ZohoOauth2Authenticator.get_auth_header", Mock(return_value={}))
    
    api = ZohoAPI(config)
    response = api.modules_settings()