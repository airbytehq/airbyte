# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from config_builder import ConfigBuilder
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from mock_server.request_builder import ZendeskChatRequestBuilder
from mock_server.response_builder import ZendeskChatResponseBuilder


_STREAM_NAME = "accounts"
_SUBDOMAIN = "d3v-airbyte"
_ACCESS_TOKEN = "any_acces_token"


def _config():
    return ConfigBuilder().subdomain(_SUBDOMAIN).build()


def _account_record():
    return {
        "account_key": "test_account_key_123",
        "status": "active",
        "create_date": "2020-01-15T10:00:00Z",
        "plan": {
            "name": "Enterprise",
            "max_agents": 100,
            "analytics": True,
        },
        "billing": {
            "email": "billing@example.com",
            "company": "Test Company",
        },
    }


class TestAccountsStream(TestCase):
    @HttpMocker()
    def test_full_refresh_returns_record(self, http_mocker: HttpMocker):
        """Test that accounts stream returns a single account record."""
        http_mocker.get(
            HttpRequest(f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/account"),
            ZendeskChatResponseBuilder.object_response(_account_record()),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["account_key"] == "test_account_key_123"
        assert output.records[0].record.data["status"] == "active"

    @HttpMocker()
    def test_404_error_is_ignored(self, http_mocker: HttpMocker):
        """Test that 404 errors are ignored per the manifest error handler configuration."""
        http_mocker.get(
            HttpRequest(f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/account"),
            ZendeskChatResponseBuilder.error_response(404, "Not Found"),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
