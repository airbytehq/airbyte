# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
import sys
from pathlib import Path

from config_builder import ConfigBuilder

from airbyte_cdk import YamlDeclarativeSource
from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_DOMAIN = "a-domain.freshdesk.com"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def test_check_succeeds_without_access_to_agents() -> None:
    """`agents` needs admin rights, so an API key that can only read tickets
    must still pass the connection check."""
    config = ConfigBuilder().domain(_DOMAIN).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), config=config)
    tickets = HttpRequest(f"https://{_DOMAIN}/api/v2/tickets", query_params=ANY_QUERY_PARAMS)
    agents = HttpRequest(f"https://{_DOMAIN}/api/v2/agents", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as http_mocker:
        http_mocker.get(tickets, HttpResponse(json.dumps([{"id": 1, "updated_at": "2026-11-01T00:00:00Z"}]), 200))
        http_mocker.get(agents, HttpResponse(json.dumps({"code": "access_denied", "message": "You are not authorized"}), 403))

        status = source.check(logging.getLogger("airbyte"), config)

        http_mocker.assert_number_of_calls(agents, 0)

    assert status.status == Status.SUCCEEDED, status.message
