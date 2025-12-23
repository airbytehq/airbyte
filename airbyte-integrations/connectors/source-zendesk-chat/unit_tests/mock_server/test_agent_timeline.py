# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from config_builder import ConfigBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from conftest import get_source


_SUBDOMAIN = "d3v-airbyte"
_STREAM_NAME = "agent_timeline"


def _config():
    return ConfigBuilder().subdomain(_SUBDOMAIN).build()


def _timeline_response(records: list, count: int = None, next_page: str = None):
    response = {
        "agent_timeline": records,
        "count": count if count is not None else len(records),
    }
    if next_page:
        response["next_page"] = next_page
    return response


class TestAgentTimelineStream(TestCase):
    @HttpMocker()
    def test_404_error_is_ignored(self, http_mocker: HttpMocker):
        """Test that 404 errors are ignored per manifest error handler."""
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/agent_timeline",
                query_params={"fields": "agent_timeline(*)", "limit": "1000", "start_time": "1443657600000000"},
            ),
            HttpResponse(body=json.dumps({"error": "Not Found"}), status_code=404),
        )

        config = _config()
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
