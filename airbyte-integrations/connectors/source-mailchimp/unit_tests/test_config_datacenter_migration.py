#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import os
from typing import Any, Mapping

import pytest
import requests
from components import ExtractAndSetDataCenterConfigValue

from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.traced_exception import FailureType


# HELPERS
def load_config(config_path: str) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


class TestExtractAndSetDataCenterConfigValue:
    """Test cases for ExtractAndSetDataCenterConfigValue."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = ExtractAndSetDataCenterConfigValue()

    def test_transform_with_existing_data_center(self):
        """Test that transform exits early if data_center already exists."""
        config = {"data_center": "us10", "credentials": {"auth_type": "oauth2.0"}}
        original_config = config.copy()

        self.extractor.transform(config)

        # Config should remain unchanged
        assert config == original_config

    def test_transform_oauth_success(self, requests_mock):
        """Test successful OAuth data center extraction."""
        requests_mock.get("https://login.mailchimp.com/oauth2/metadata", json={"dc": "us10"})

        config = {"credentials": {"auth_type": "oauth2.0", "access_token": "test_token"}}

        self.extractor.transform(config)

        assert config.get("data_center") == "us10"

    def test_transform_oauth_invalid_token(self, requests_mock):
        """Test OAuth invalid token error handling."""
        requests_mock.get("https://login.mailchimp.com/oauth2/metadata", json={"error": "invalid_token"})

        config = {"credentials": {"auth_type": "oauth2.0", "access_token": "invalid_token"}}

        with pytest.raises(AirbyteTracedException) as exc_info:
            self.extractor.transform(config)

        assert exc_info.value.failure_type == FailureType.config_error
        assert "invalid" in exc_info.value.message.lower()

    def test_transform_oauth_network_error(self, requests_mock):
        """Test OAuth network error handling."""
        requests_mock.get("https://login.mailchimp.com/oauth2/metadata", exc=requests.exceptions.RequestException("Network error"))

        config = {"credentials": {"auth_type": "oauth2.0", "access_token": "test_token"}}

        with pytest.raises(AirbyteTracedException) as exc_info:
            self.extractor.transform(config)

        assert exc_info.value.failure_type == FailureType.config_error
        assert "Unable to extract data center" in exc_info.value.message

    def test_transform_apikey_credentials_success(self):
        """Test successful API key data center extraction from credentials."""
        config = {"credentials": {"auth_type": "apikey", "apikey": "test_key-us20"}}

        self.extractor.transform(config)

        assert config.get("data_center") == "us20"

    def test_transform_apikey_top_level_success(self):
        """Test successful API key data center extraction from top level (backward compatibility)."""
        config = {"apikey": "test_key-us30"}

        self.extractor.transform(config)

        assert config.get("data_center") == "us30"

    def test_transform_oauth_http_error(self, requests_mock):
        """Test OAuth HTTP error handling."""
        requests_mock.get("https://login.mailchimp.com/oauth2/metadata", status_code=500)

        config = {"credentials": {"auth_type": "oauth2.0", "access_token": "test_token"}}

        with pytest.raises(AirbyteTracedException) as exc_info:
            self.extractor.transform(config)

        assert exc_info.value.failure_type == FailureType.config_error
        assert "Unable to extract data center" in exc_info.value.message


class TestExtractAndSetDataCenterConfigValueIntegration:
    """Integration tests using actual config files."""

    @pytest.mark.parametrize(
        "config_path,expected_data_center",
        [
            ("test_configs/test_config_api_key.json", "us10"),
            ("test_configs/test_config_oauth.json", "us10"),
        ],
        ids=["api_key_config", "oauth_config"],
    )
    def test_config_file_integration(self, config_path, expected_data_center, requests_mock):
        """Test integration with actual config files."""
        # Mock OAuth endpoint for OAuth config
        requests_mock.get("https://login.mailchimp.com/oauth2/metadata", json={"dc": expected_data_center})

        config_path = os.path.join(os.path.dirname(__file__), config_path)
        config = load_config(config_path)

        # Remove existing data_center to test extraction
        if "data_center" in config:
            del config["data_center"]

        extractor = ExtractAndSetDataCenterConfigValue()
        extractor.transform(config)

        assert config.get("data_center") == expected_data_center
