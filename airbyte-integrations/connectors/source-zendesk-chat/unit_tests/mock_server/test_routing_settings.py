# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from config_builder import ConfigBuilder
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "routing_settings"
_SUBDOMAIN = "d3v-airbyte"


def _config():
    return ConfigBuilder().subdomain(_SUBDOMAIN).build()


def _routing_settings_record():
    return {
        "enabled": True,
        "max_queue_size": 10,
        "skill_routing": {"enabled": True, "max_wait_time": 60},
        "reassignment": {"enabled": False, "timeout": 300},
    }


class TestRoutingSettingsStream(TestCase):
    @HttpMocker()
    def test_full_refresh_returns_record(self, http_mocker: HttpMocker):
        """Test that routing_settings stream returns settings wrapped in data field."""
        http_mocker.get(
            HttpRequest(f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/routing_settings/account"),
            HttpResponse(
                body=json.dumps({"data": _routing_settings_record()}),
                status_code=200,
            ),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["enabled"] is True
        assert output.records[0].record.data["max_queue_size"] == 10

    @HttpMocker()
    def test_404_error_is_ignored(self, http_mocker: HttpMocker):
        """Test that 404 errors are ignored per the manifest error handler configuration."""
        http_mocker.get(
            HttpRequest(f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/routing_settings/account"),
            HttpResponse(
                body=json.dumps({"error": {"message": "Not Found"}}),
                status_code=404,
            ),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
