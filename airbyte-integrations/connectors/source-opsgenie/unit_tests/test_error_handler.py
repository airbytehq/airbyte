# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Iterator
from unittest import TestCase
from unittest.mock import patch

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_CONFIG = {"api_token": "test-token", "endpoint": "api.opsgenie.com", "start_date": "2024-01-01T00:00:00Z"}
_TEAMS_REQUEST = HttpRequest("https://api.opsgenie.com/v2/teams")
_MAX_RETRIES = 5


def _error_handlers(node: Any) -> Iterator[dict]:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("error_handler", "on_error") and isinstance(value, dict):
                yield value
            yield from _error_handlers(value)
    elif isinstance(node, list):
        for item in node:
            yield from _error_handlers(item)


def _teams_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"data": [{"id": "team-1", "name": "Team 1"}]}), status_code=200)


def _read(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("teams", SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog, expecting_exception=expecting_exception)


def test_every_error_handler_is_a_rate_limit_aware_default_error_handler() -> None:
    manifest = yaml.safe_load(Path(_YAML_FILE_PATH).read_text())
    handlers = list(_error_handlers(manifest))

    assert len(handlers) == 28
    for handler in handlers:
        assert handler["type"] == "DefaultErrorHandler"
        assert [(strategy["type"], strategy["header"]) for strategy in handler["backoff_strategies"]] == [
            ("WaitUntilTimeFromHeader", "X-RateLimit-Period-In-Sec")
        ]


@patch("time.sleep", lambda _: None)
class TestTeamsErrorHandler(TestCase):
    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _TEAMS_REQUEST,
            [HttpResponse(body="", status_code=429, headers={"X-RateLimit-Period-In-Sec": "1"}), _teams_response()],
        )

        output = _read()

        assert [record.record.data["id"] for record in output.records] == ["team-1"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_TEAMS_REQUEST, 2)

    @HttpMocker()
    def test_5xx_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_TEAMS_REQUEST, [HttpResponse(body="", status_code=500), _teams_response()])

        output = _read()

        assert [record.record.data["id"] for record in output.records] == ["team-1"]
        http_mocker.assert_number_of_calls(_TEAMS_REQUEST, 2)

    @HttpMocker()
    def test_persistent_5xx_stops_after_max_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_TEAMS_REQUEST, HttpResponse(body="", status_code=500))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_TEAMS_REQUEST, _MAX_RETRIES + 1)

    @HttpMocker()
    def test_403_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_TEAMS_REQUEST, HttpResponse(body="", status_code=403))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_TEAMS_REQUEST, 1)
