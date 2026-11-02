# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import freezegun
import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {
    "aws_key_id": "test-key-id",
    "aws_secret_key": "test-secret-key",
    "aws_region_name": "us-east-1",
    "start_date": "2026-10-01",
}
_START_TIME = 1790812800  # 2026-10-01T00:00:00Z, from start_date
_NOW = 1790899200  # 2026-10-02T00:00:00Z, the frozen current time
_LOOKUP_EVENTS_REQUEST = HttpRequest(
    url="https://cloudtrail.us-east-1.amazonaws.com/",
    headers={"x-amz-target": "com.amazonaws.cloudtrail.v20131101.CloudTrail_20131101.LookupEvents"},
    body={"MaxResults": 50, "StartTime": _START_TIME, "EndTime": _NOW},
)
_EVENT = {"EventId": "event-1", "EventName": "ConsoleLogin", "EventTime": 1790856000.0}


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _find_typed_nodes(node, type_name):
    if isinstance(node, dict):
        if node.get("type") == type_name:
            yield node
        for value in node.values():
            yield from _find_typed_nodes(value, type_name)
    elif isinstance(node, list):
        for value in node:
            yield from _find_typed_nodes(value, type_name)


def _read_management_events():
    catalog = (
        CatalogBuilder()
        .with_stream(ConfiguredAirbyteStreamBuilder().with_name("management_events").with_sync_mode(SyncMode.full_refresh))
        .build()
    )
    return read(get_source(_CONFIG), _CONFIG, catalog)


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())

    assert list(_find_typed_nodes(manifest, "CompositeErrorHandler")) == []


def test_error_handlers_retry_http_400_with_exponential_backoff() -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    error_handlers = [requester["error_handler"] for requester in _find_typed_nodes(manifest, "HttpRequester")]

    assert len(error_handlers) == 3
    for error_handler in error_handlers:
        assert error_handler == {
            "type": "DefaultErrorHandler",
            "backoff_strategies": [{"type": "ExponentialBackoffStrategy"}],
            "response_filters": [{"type": "HttpResponseFilter", "action": "RETRY", "http_codes": [400]}],
        }


@freezegun.freeze_time("2026-10-02T00:00:00Z")
def test_management_events_retries_http_400_then_completes() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.post(
            _LOOKUP_EVENTS_REQUEST,
            [
                HttpResponse(json.dumps({"__type": "ThrottlingException", "message": "Rate exceeded"}), 400),
                HttpResponse(json.dumps({"Events": [_EVENT]}), 200),
            ],
        )

        output = _read_management_events()

        http_mocker.assert_number_of_calls(_LOOKUP_EVENTS_REQUEST, 2)
    assert not output.errors
