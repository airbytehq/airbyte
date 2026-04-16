#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import requests_mock as req_mock
from source_etrade.source import SourceEtrade


class TestSourceEtrade:
    def test_check_connection_success(self, config):
        source = SourceEtrade()
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/list",
                json={
                    "AccountListResponse": {
                        "Accounts": {
                            "Account": [
                                {
                                    "accountId": "12345678",
                                    "accountIdKey": "abc123",
                                    "accountStatus": "ACTIVE",
                                }
                            ]
                        }
                    }
                },
            )
            ok, error = source.check_connection(None, config)
            assert ok is True
            assert error is None

    def test_check_connection_auth_failure(self, config):
        source = SourceEtrade()
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/list",
                status_code=401,
            )
            ok, error = source.check_connection(None, config)
            assert ok is False
            assert "Authentication failed" in error

    def test_check_connection_forbidden(self, config):
        source = SourceEtrade()
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/list",
                status_code=403,
            )
            ok, error = source.check_connection(None, config)
            assert ok is False
            assert "Access forbidden" in error

    def test_get_base_url_sandbox(self, config):
        config["sandbox"] = True
        assert SourceEtrade._get_base_url(config) == "https://apisb.etrade.com"

    def test_get_base_url_live(self, config):
        config["sandbox"] = False
        assert SourceEtrade._get_base_url(config) == "https://api.etrade.com"

    def test_get_start_date_from_config(self, config):
        config["start_date"] = "2024-06-01"
        assert SourceEtrade._get_start_date(config) == "2024-06-01"

    def test_get_start_date_default(self, config):
        config.pop("start_date", None)
        start_date = SourceEtrade._get_start_date(config)
        # Should be approximately 2 years ago
        assert len(start_date) == 10
        assert start_date[4] == "-"

    def test_streams_count(self, config):
        source = SourceEtrade()
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/list",
                json={
                    "AccountListResponse": {
                        "Accounts": {
                            "Account": [
                                {"accountIdKey": "abc123"},
                            ]
                        }
                    }
                },
            )
            streams = source.streams(config)
            assert len(streams) == 10

    def test_spec(self):
        source = SourceEtrade()
        spec = source.spec(None)
        assert spec is not None
        connection_spec = spec.connectionSpecification
        assert "consumer_key" in connection_spec["properties"]
        assert "consumer_secret" in connection_spec["properties"]
        assert "oauth_token" in connection_spec["properties"]
        assert "oauth_token_secret" in connection_spec["properties"]
        assert "sandbox" in connection_spec["properties"]

    def test_get_account_id_keys_from_config(self, config):
        config["account_id_keys"] = ["key1", "key2"]
        source = SourceEtrade()
        keys = source._get_account_id_keys(config)
        assert keys == ["key1", "key2"]

    def test_get_account_id_keys_from_api(self, config):
        config["account_id_keys"] = []
        source = SourceEtrade()
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/list",
                json={
                    "AccountListResponse": {
                        "Accounts": {
                            "Account": [
                                {"accountIdKey": "abc123"},
                                {"accountIdKey": "def456"},
                            ]
                        }
                    }
                },
            )
            keys = source._get_account_id_keys(config)
            assert keys == ["abc123", "def456"]
