#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import os
from typing import Any, Mapping
from unittest.mock import patch

import pytest

from .conftest import get_source


TEST_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_config.json"


@pytest.fixture(autouse=True)
def mock_is_cloud_environment():
    with patch("airbyte_cdk.utils.is_cloud_environment", return_value=True):
        yield


class TestMigrations:
    @pytest.mark.parametrize(
        "key_to_migrate, migrated_key",
        [
            ("groups", "groups_list"),
            ("projects", "projects_list"),
        ],
        ids=["groups-migration", "projects-migration"],
    )
    def test_migrations(self, key_to_migrate, migrated_key):
        try:
            with open(TEST_CONFIG_PATH, "r") as f:
                config: Mapping[str, Any] = json.load(f)
            assert config[key_to_migrate] == "a b c"
            assert not config.get(migrated_key)
            source = get_source(config=config, config_path=TEST_CONFIG_PATH)
            migrated_config = source.configure(config=config, temp_dir="/not/a/real/path")
            assert migrated_config[migrated_key] == ["a", "b", "c"]
        finally:
            with open(TEST_CONFIG_PATH, "w") as f:
                json.dump(config, f)

    def test_given_no_key_to_migrate_then_no_migration_is_performed(self):
        try:
            with open(TEST_CONFIG_PATH, "r") as f:
                config: Mapping[str, Any] = json.load(f)
            copy_config = dict(config)
            copy_config["groups"] = None
            source = get_source(config=copy_config, config_path=TEST_CONFIG_PATH)
            migrated_config = source.configure(config=copy_config, temp_dir="/not/a/real/path")
            assert not migrated_config.get("groups_list")
            assert migrated_config["groups"] == None
            assert migrated_config.get("projects_list")
        finally:
            with open(TEST_CONFIG_PATH, "w") as f:
                json.dump(config, f)


class TestValidations:
    def test_given_valid_api_url_then_no_exception_is_raised(self, oauth_config):
        config = dict(oauth_config)
        config["api_url"] = "https://gitlab.com"
        source = get_source(config=config, config_path=None)
        migrated_config = source.configure(config=config, temp_dir="/not/a/real/path")
        source.streams(migrated_config)

    @pytest.mark.parametrize(
        "invalid_api_url, expected_error",
        [
            ("http://badscheme.com", "Http scheme is not allowed in this environment. Please use `https` instead."),
            ("not a valid url", "Invalid API resource locator."),
            ("gitlab.com/api/v2/resource", "Invalid API resource locator."),
        ],
        ids=["bad-scheme", "invalid-url-string", "invalid-url-format"],
    )
    def test_given_invalid_api_url_then_exception_is_raised(self, mock_is_cloud_environment, oauth_config, invalid_api_url, expected_error):
        config = dict(oauth_config)
        config["api_url"] = invalid_api_url
        source = get_source(config=config, config_path=None)
        migrated_config = source.configure(config=config, temp_dir="/not/a/real/path")
        with pytest.raises(ValueError) as e:
            source.streams(migrated_config)
        assert str(e.value) == expected_error
