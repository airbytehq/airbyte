# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from config_builder import ConfigBuilder
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from mock_server.response_builder import ZendeskChatResponseBuilder


_STREAM_NAME = "triggers"
_SUBDOMAIN = "d3v-airbyte"


def _config():
    return ConfigBuilder().subdomain(_SUBDOMAIN).build()


def _trigger_record(trigger_id: int, name: str):
    return {
        "id": trigger_id,
        "name": name,
        "description": f"Description for {name}",
        "enabled": True,
        "definition": {"event": "chat_start", "actions": []},
    }


class TestTriggersStream(TestCase):
    @HttpMocker()
    def test_full_refresh_returns_records(self, http_mocker: HttpMocker):
        """Test that triggers stream returns array of trigger records."""
        records = [
            _trigger_record(1, "Welcome Trigger"),
            _trigger_record(2, "Proactive Chat"),
        ]
        http_mocker.get(
            HttpRequest(f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/triggers"),
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
            HttpRequest(f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/triggers"),
            ZendeskChatResponseBuilder.error_response(404, "Not Found"),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
