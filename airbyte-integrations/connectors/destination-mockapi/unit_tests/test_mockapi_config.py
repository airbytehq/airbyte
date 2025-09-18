# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import pytest
from destination_mockapi.config import MockAPIConfig, get_config_from_dict
from pydantic import ValidationError


class TestMockAPIConfig:
    def test_config_with_real_api_url(self):
        """Test configuration with real API URL from config"""
        config = MockAPIConfig(api_url="https://68cc13e1716562cf50764f2b.mockapi.io/api/v1", batch_size=50, timeout=30)
        assert config.api_url == "https://68cc13e1716562cf50764f2b.mockapi.io/api/v1"
        assert config.batch_size == 50
        assert config.timeout == 30

    def test_config_from_secrets_dict(self):
        """Test creating config from secrets/config.json structure"""
        config_dict = {"api_url": "https://68cc13e1716562cf50764f2b.mockapi.io/api/v1"}
        config = get_config_from_dict(config_dict)
        assert config.api_url == "https://68cc13e1716562cf50764f2b.mockapi.io/api/v1"
        assert config.batch_size == 100  # default value
        assert config.timeout == 30  # default value

    def test_url_validation(self):
        """Test URL validation"""
        with pytest.raises(ValidationError):
            MockAPIConfig(api_url="invalid-url")

    def test_url_trailing_slash_removal(self):
        """Test that trailing slashes are removed"""
        config = MockAPIConfig(api_url="https://68cc13e1716562cf50764f2b.mockapi.io/api/v1/")
        assert config.api_url == "https://68cc13e1716562cf50764f2b.mockapi.io/api/v1"
