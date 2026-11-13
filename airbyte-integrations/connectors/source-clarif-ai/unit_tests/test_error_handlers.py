# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import re
import time

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "api_key": "test_api_key",
    "user_id": "test_user_id",
    "start_date": "2024-01-01T00:00:00Z",
}
_STREAM_NAMES = (
    "applications",
    "datasets",
    "models",
    "model_versions",
    "worklows",
    "app_inputs",
    "app_inputs_jobs",
    "app_concepts",
)


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_streams_use_default_error_handler(stream_name):
    manifest = get_source(_CONFIG).resolved_manifest
    error_handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler["type"] == "DefaultErrorHandler"
    assert error_handler["max_retries"] == 3
    assert [{"type": strategy["type"], "factor": strategy["factor"]} for strategy in error_handler["backoff_strategies"]] == [
        {"type": "ExponentialBackoffStrategy", "factor": 2}
    ]

    response_filters = error_handler["response_filters"]
    assert len(response_filters) == 1
    assert {
        "type": response_filters[0]["type"],
        "action": response_filters[0]["action"],
        "http_codes": response_filters[0]["http_codes"],
        "error_message": response_filters[0]["error_message"],
    } == {
        "type": "HttpResponseFilter",
        "action": "RATE_LIMITED",
        "http_codes": [429],
        "error_message": "Rate limits has been hit",
    }


def test_applications_retries_rate_limited_response(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)
    config = _CONFIG
    catalog = CatalogBuilder().with_stream("applications", SyncMode.full_refresh).build()

    with requests_mock.Mocker() as mocker:
        response = mocker.get(
            re.compile(r"https://api\.clarifai\.com/v2/users/test_user_id/apps(?:\?.*)?"),
            [
                {"status_code": 429, "json": {"error": "rate limited"}},
                {"status_code": 200, "json": {"apps": [{"id": "app1"}]}},
            ],
        )
        output = read(get_source(config), config=config, catalog=catalog)

    assert len(output.records) == 1
    assert response.call_count == 2
