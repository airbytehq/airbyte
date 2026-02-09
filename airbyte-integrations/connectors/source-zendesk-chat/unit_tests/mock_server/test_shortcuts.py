# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from config_builder import ConfigBuilder
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from mock_server.response_builder import ZendeskChatResponseBuilder


_STREAM_NAME = "shortcuts"
_SUBDOMAIN = "d3v-airbyte"


def _config():
    return ConfigBuilder().subdomain(_SUBDOMAIN).build()


def _shortcut_record(shortcut_id: int, name: str):
    return {
        "id": shortcut_id,
        "name": name,
        "message": f"This is the message for {name}",
        "options": "greeting",
        "tags": ["support", "quick"],
    }


class TestShortcutsStream(TestCase):
    @HttpMocker()
    def test_full_refresh_returns_records(self, http_mocker: HttpMocker):
        """Test that shortcuts stream returns array of shortcut records."""
        records = [
            _shortcut_record(1, "greeting"),
            _shortcut_record(2, "farewell"),
        ]
        http_mocker.get(
            HttpRequest(f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/shortcuts"),
            ZendeskChatResponseBuilder.array_response(records),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert {r.record.data["id"] for r in output.records} == {1, 2}

    @HttpMocker()
    def test_404_error_is_ignored(self, http_mocker: HttpMocker):
        """Test that 404 errors are ignored per the manifest error handler configuration."""
        http_mocker.get(
            HttpRequest(f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/shortcuts"),
            ZendeskChatResponseBuilder.error_response(404, "Not Found"),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
