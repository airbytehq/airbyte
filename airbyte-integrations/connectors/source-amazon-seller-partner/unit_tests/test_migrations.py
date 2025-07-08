#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path
from typing import Any, Mapping

import pytest

from .conftest import get_source


MIGRATIONS_TEST_DIRECTORY = Path(__file__).parent / "test_migrations"


def load_config(config_path: Path) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


UNMIGRATED_CONFIG = {
    "refresh_token": "refresh_token",
    "lwa_app_id": "amzn1.application-oa2-client.lwa_app_id",
    "lwa_client_secret": "amzn1.oa2-cs.v1.lwa_client_secret",
    "replication_start_date": "2022-09-01T00:00:00Z",
    "aws_environment": "PRODUCTION",
    "region": "US",
    "report_options": '{"GET_REPORT": {"reportPeriod": "WEEK"}, "GET_REPORT_2": {"reportPeriod_2": "DAY"}}',
}

MIGRATED_CONFIG = {
    "refresh_token": "refresh_token",
    "lwa_app_id": "amzn1.application-oa2-client.lwa_app_id",
    "lwa_client_secret": "amzn1.oa2-cs.v1.lwa_client_secret",
    "replication_start_date": "2022-09-01T00:00:00Z",
    "aws_environment": "PRODUCTION",
    "region": "US",
    "report_options_list": [
        {
            "report_name": "TEST_REPORT_1",
            "stream_name": "GET_REPORT_1",
            "options_list": [{"option_name": "reportPeriod", "option_value": "WEEK"}],
        },
        {
            "report_name": "TEST_REPORT_2",
            "stream_name": "GET_REPORT_2",
            "options_list": [{"option_name": "reportPeriod", "option_value": "WEEK"}],
        },
    ],
    "account_type": "Vendor",
}

INVALID_STREAM_NAMES_CONFIG = {
    "refresh_token": "refresh_token",
    "lwa_app_id": "amzn1.application-oa2-client.lwa_app_id",
    "lwa_client_secret": "amzn1.oa2-cs.v1.lwa_client_secret",
    "replication_start_date": "2022-09-01T00:00:00Z",
    "aws_environment": "PRODUCTION",
    "region": "US",
    "report_options_list": [
        {
            "report_name": "report_name",
            "stream_name": "duplicate_stream_name",
            "options_list": [{"option_name": "reportPeriod", "option_value": "WEEK"}],
        },
        {
            "report_name": "report_name",
            "stream_name": "duplicate_stream_name",
            "options_list": [{"option_name": "reportPeriod_2", "option_value": "DAY"}],
        },
    ],
    "account_type": "Vendor",
}

INVALID_OPTION_NAMES_CONFIG = {
    "refresh_token": "refresh_token",
    "lwa_app_id": "amzn1.application-oa2-client.lwa_app_id",
    "lwa_client_secret": "amzn1.oa2-cs.v1.lwa_client_secret",
    "replication_start_date": "2022-09-01T00:00:00Z",
    "aws_environment": "PRODUCTION",
    "region": "US",
    "report_options_list": [
        {
            "report_name": "report_name_1",
            "stream_name": "stream_1",
            "options_list": [
                {"option_name": "reportPeriod", "option_value": "WEEK"},
                {"option_name": "reportPeriod", "option_value": "DAY"},
            ],
        },
    ],
    "account_type": "Vendor",
}

CONFIG_WITHOUT_REPORT_OPTIONS_LIST = {
    "refresh_token": "refresh_token",
    "lwa_app_id": "amzn1.application-oa2-client.lwa_app_id",
    "lwa_client_secret": "amzn1.oa2-cs.v1.lwa_client_secret",
    "replication_start_date": "2022-09-01T00:00:00Z",
    "aws_environment": "PRODUCTION",
    "region": "US",
    "account_type": "Vendor",
}


class TestMigrations:
    test_unmigrated_config_path = MIGRATIONS_TEST_DIRECTORY / "unmigrated_config.json"
    test_migrated_config_path = MIGRATIONS_TEST_DIRECTORY / "migrated_config.json"

    def test_migrate_config(self, components_module):
        try:
            config_copy = dict(UNMIGRATED_CONFIG)
            assert "account_type" not in config_copy
            get_source(config_copy, config_path=str(self.test_unmigrated_config_path))
            migrated_config = load_config(self.test_unmigrated_config_path)
            assert migrated_config["account_type"] == "Seller"
            assert isinstance(migrated_config["report_options_list"], list)
            assert len(migrated_config["report_options_list"]) == 2
            assert migrated_config["report_options_list"][0]["report_name"] == "GET_REPORT"
            assert migrated_config["report_options_list"][0]["stream_name"] == "GET_REPORT"
            assert migrated_config["report_options_list"][0]["options_list"][0]["option_name"] == "reportPeriod"
            assert migrated_config["report_options_list"][0]["options_list"][0]["option_value"] == "WEEK"
            assert migrated_config["report_options_list"][1]["report_name"] == "GET_REPORT_2"
            assert migrated_config["report_options_list"][1]["stream_name"] == "GET_REPORT_2"
            assert migrated_config["report_options_list"][1]["options_list"][0]["option_name"] == "reportPeriod_2"
            assert migrated_config["report_options_list"][1]["options_list"][0]["option_value"] == "DAY"
        finally:
            with self.test_unmigrated_config_path.open("w") as f:
                json.dump(config_copy, f)

    def test_already_migrated_config(self, components_module):
        try:
            config_copy = dict(MIGRATED_CONFIG)
            get_source(config_copy, config_path=str(self.test_migrated_config_path))
            migrated_config = load_config(self.test_migrated_config_path)
            print("migrated_config", migrated_config)
            assert migrated_config["account_type"] == "Vendor"
            assert migrated_config["report_options_list"] == MIGRATED_CONFIG["report_options_list"]
            assert migrated_config["report_options_list"][0]["report_name"] == MIGRATED_CONFIG["report_options_list"][0]["report_name"]
            assert migrated_config["report_options_list"][0]["stream_name"] == MIGRATED_CONFIG["report_options_list"][0]["stream_name"]
            assert (
                migrated_config["report_options_list"][0]["options_list"][0]["option_name"]
                == MIGRATED_CONFIG["report_options_list"][0]["options_list"][0]["option_name"]
            )
            assert (
                migrated_config["report_options_list"][0]["options_list"][0]["option_value"]
                == MIGRATED_CONFIG["report_options_list"][0]["options_list"][0]["option_value"]
            )
            assert migrated_config["report_options_list"][1]["report_name"] == MIGRATED_CONFIG["report_options_list"][1]["report_name"]
            assert migrated_config["report_options_list"][1]["stream_name"] == MIGRATED_CONFIG["report_options_list"][1]["stream_name"]
            assert (
                migrated_config["report_options_list"][1]["options_list"][0]["option_name"]
                == MIGRATED_CONFIG["report_options_list"][1]["options_list"][0]["option_name"]
            )
            assert (
                migrated_config["report_options_list"][1]["options_list"][0]["option_value"]
                == MIGRATED_CONFIG["report_options_list"][1]["options_list"][0]["option_value"]
            )
        finally:
            with self.test_migrated_config_path.open("w") as f:
                json.dump(config_copy, f)


class TestTransformations:
    def test_transformation(self):
        config_1 = dict(MIGRATED_CONFIG)
        config_2 = dict(MIGRATED_CONFIG)
        config_2["aws_environment"] = "SANDBOX"
        config_2["region"] = "SA"
        source_1 = get_source(config_1)
        source_2 = get_source(config_2)

        # PRODUCTION, US
        assert source_1._config["endpoint"] == "https://sellingpartnerapi-na.amazon.com"
        assert source_1._config["marketplace_id"] == "ATVPDKIKX0DER"

        # SANDBOX, SA
        assert source_2._config["endpoint"] == "https://sandbox.sellingpartnerapi-eu.amazon.com"
        assert source_2._config["marketplace_id"] == "A17E79C6D8DWNP"


class TestValidations:
    @pytest.mark.parametrize("config", [INVALID_STREAM_NAMES_CONFIG, INVALID_OPTION_NAMES_CONFIG])
    def test_given_invalid_config_then_it_should_raise_error(self, config):
        source = get_source(config)
        with pytest.raises(ValueError) as e:
            source.streams(config)
        assert "should be unique across all" in str(e.value)

    @pytest.mark.parametrize("config", [MIGRATED_CONFIG, CONFIG_WITHOUT_REPORT_OPTIONS_LIST])
    def test_given_valid_config_then_it_should_not_raise_error(self, config):
        source = get_source(config)
        source.streams(config)
