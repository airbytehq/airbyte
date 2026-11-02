# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for VWO stream error handlers."""

import json
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

import pytest
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_STREAM_NAMES = [
    "accounts",
    "accounts_feeds",
    "users",
    "smartcode",
    "campaigns",
    "custom_widgets",
    "thresholds",
    "integrations",
    "labels",
]
_EXPECTED_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "max_retries": 3,
    "backoff_strategies": [{"type": "ExponentialBackoffStrategy", "factor": 2}],
    "response_filters": [
        {
            "type": "HttpResponseFilter",
            "action": "RATE_LIMITED",
            "http_codes": [429],
            "error_message": "Rate limits hit",
        }
    ],
}
_STREAM_NAME = "labels"
_BASE_URL = "https://app.vwo.com/api/v2"
_CONFIG = {"api_key": "test-key", "start_date": "2024-01-01T00:00:00Z"}
_LABEL_REQUEST = HttpRequest(
    url=f"{_BASE_URL}/accounts/current/labels",
    query_params={"offset": "0", "limit": "50"},
)


def _label(label_id: int) -> Dict[str, Any]:
    return {"id": label_id, "name": f"label-{label_id}"}


def _labels_response(*labels: Dict[str, Any]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"_data": list(labels)}), status_code=200)


def _read_labels(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_streams_use_default_error_handler(stream_name: str) -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())

    assert manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"] == _EXPECTED_ERROR_HANDLER


def test_manifest_does_not_use_composite_error_handler() -> None:
    assert "".join(("Composite", "ErrorHandler")) not in _YAML_FILE_PATH.read_text()


@patch("time.sleep", lambda _: None)
class TestVwoErrorHandler(TestCase):
    @HttpMocker()
    def test_labels_records_are_emitted(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_LABEL_REQUEST, _labels_response(_label(1)))

        output = _read_labels()

        assert [record.record.data["id"] for record in output.records] == [1]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_LABEL_REQUEST, 1)

    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _LABEL_REQUEST,
            [
                HttpResponse(body="", status_code=429),
                _labels_response(_label(1)),
            ],
        )

        output = _read_labels()

        assert [record.record.data["id"] for record in output.records] == [1]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_LABEL_REQUEST, 2)

    @HttpMocker()
    def test_429_exhausts_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _LABEL_REQUEST,
            [HttpResponse(body="", status_code=429) for _ in range(4)],
        )

        output = _read_labels(expecting_exception=True)

        assert output.errors
        http_mocker.assert_number_of_calls(_LABEL_REQUEST, 4)
