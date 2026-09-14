# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from config_builder import ConfigBuilder
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from mock_server.response_builder import ZendeskChatResponseBuilder


_STREAM_NAME = "departments"
_SUBDOMAIN = "d3v-airbyte"


def _config():
    return ConfigBuilder().subdomain(_SUBDOMAIN).build()


def _department_record(department_id: int, name: str):
    return {
        "id": department_id,
        "name": name,
        "description": f"Description for {name}",
        "enabled": True,
        "members": [1, 2, 3],
        "settings": {"chat_enabled": True},
    }


class TestDepartmentsStream(TestCase):
    @HttpMocker()
    def test_full_refresh_returns_records(self, http_mocker: HttpMocker):
        """Test that departments stream returns array of department records."""
        records = [
            _department_record(1, "Sales"),
            _department_record(2, "Support"),
        ]
        http_mocker.get(
            HttpRequest(f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/departments"),
            ZendeskChatResponseBuilder.array_response(records),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert {r.record.data["id"] for r in output.records} == {1, 2}
        assert output.records[0].record.data["name"] in ["Sales", "Support"]

    @HttpMocker()
    def test_404_error_is_ignored(self, http_mocker: HttpMocker):
        """Test that 404 errors are ignored per the manifest error handler configuration."""
        http_mocker.get(
            HttpRequest(f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/departments"),
            ZendeskChatResponseBuilder.error_response(404, "Not Found"),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
