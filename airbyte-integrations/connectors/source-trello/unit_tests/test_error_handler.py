# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for Trello error-handler behavior."""

import json
from unittest.mock import patch

import yaml
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {
    "key": "test-key",
    "token": "test-token",
    "start_date": "2024-01-01T00:00:00Z",
    "board_ids": [],
}
_BOARDS_ENDPOINT = "https://api.trello.com/1/members/me/boards"
_BOARD_ID = "012345678901234567890123"
_START_DATE = _CONFIG["start_date"]


def _boards_request() -> HttpRequest:
    return HttpRequest(
        url=_BOARDS_ENDPOINT,
        query_params={"since": _START_DATE},
    )


def _boards_response(*boards: dict) -> HttpResponse:
    return HttpResponse(body=json.dumps(list(boards)), status_code=200)


def _read_boards(expecting_exception: bool = False):
    catalog = CatalogBuilder().with_stream("boards", SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        config=_CONFIG,
        catalog=catalog,
        expecting_exception=expecting_exception,
    )


def _iter_error_handlers(value):
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if key == "error_handler":
                yield nested_value
            yield from _iter_error_handlers(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            yield from _iter_error_handlers(nested_value)


def _iter_error_handler_types(value):
    if isinstance(value, dict):
        if str(value.get("type", "")).endswith("ErrorHandler"):
            yield value["type"]
        for nested_value in value.values():
            yield from _iter_error_handler_types(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            yield from _iter_error_handler_types(nested_value)


def test_manifest_uses_only_default_error_handlers() -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    handlers = list(_iter_error_handlers(manifest))

    assert len(handlers) == 37
    assert (
        handlers
        == [
            {
                "type": "DefaultErrorHandler",
                "backoff_strategies": [{"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 10}],
            }
        ]
        * 37
    )
    assert set(_iter_error_handler_types(manifest)) == {"DefaultErrorHandler"}


@HttpMocker()
def test_429_retries_then_emits_board(http_mocker: HttpMocker) -> None:
    first_request = _boards_request()
    board = {"id": _BOARD_ID, "name": "Test board"}
    http_mocker.get(
        first_request,
        [
            HttpResponse(body="", status_code=429),
            _boards_response(board),
        ],
    )

    with patch("time.sleep") as mocked_sleep:
        output = _read_boards()

    assert [record.record.data for record in output.records] == [board]
    assert output.errors == []
    http_mocker.assert_number_of_calls(first_request, 2)
    mocked_sleep.assert_any_call(11)


@HttpMocker()
def test_403_fails_without_retry(http_mocker: HttpMocker) -> None:
    first_request = _boards_request()
    http_mocker.get(first_request, HttpResponse(body='{"message": "Forbidden"}', status_code=403))

    output = _read_boards(expecting_exception=True)

    assert output.records == []
    assert output.errors
    http_mocker.assert_number_of_calls(first_request, 1)
