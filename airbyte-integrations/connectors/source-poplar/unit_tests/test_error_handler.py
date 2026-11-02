# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_CONFIG = {"access_token": "test-token", "start_date": "2024-01-01T00:00:00Z"}
_CAMPAIGNS_REQUEST = HttpRequest("https://api.heypoplar.com/v1/campaigns")
_ME_REQUEST = HttpRequest("https://api.heypoplar.com/v1/me")
_CAMPAIGN_RECORD = {"id": "campaign-1", "name": "Campaign 1"}
_MAX_RETRIES = 10
_EXPECTED_FILTERED_ERROR_HANDLER = {
    "$ref": "#/definitions/rate_limit_error_handler",
    "response_filters": [
        {
            "type": "HttpResponseFilter",
            "action": "IGNORE",
            "http_codes": [403],
            "error_message": "Forbidden",
        }
    ],
}


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


def test_stream_error_handlers_are_unwrapped() -> None:
    manifest = yaml.safe_load(Path(_YAML_FILE_PATH).read_text())
    streams = manifest["definitions"]["streams"]

    for stream_name in ("campaigns", "audiences", "mailings", "me"):
        error_handler = streams[stream_name]["retriever"]["requester"]["error_handler"]
        assert error_handler == _EXPECTED_FILTERED_ERROR_HANDLER

    creatives_error_handler = streams["creatives"]["retriever"]["requester"]["error_handler"]
    assert creatives_error_handler == {"$ref": "#/definitions/rate_limit_error_handler"}


@patch("time.sleep", lambda _: None)
class TestCampaignsErrorHandler(TestCase):
    @HttpMocker()
    def test_403_is_ignored(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_CAMPAIGNS_REQUEST, HttpResponse(body="", status_code=403))

        output = _read("campaigns")

        assert output.records == []
        assert output.errors == []
        http_mocker.assert_number_of_calls(_CAMPAIGNS_REQUEST, 1)

    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _CAMPAIGNS_REQUEST,
            [
                HttpResponse(body="", status_code=429, headers={"ratelimit-reset": "1"}),
                HttpResponse(body=json.dumps([_CAMPAIGN_RECORD]), status_code=200),
            ],
        )

        output = _read("campaigns")

        assert [record.record.data for record in output.records] == [_CAMPAIGN_RECORD]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_CAMPAIGNS_REQUEST, 2)

    @HttpMocker()
    def test_persistent_500_stops_after_max_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_CAMPAIGNS_REQUEST, HttpResponse(body="", status_code=500))

        output = _read("campaigns", expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_CAMPAIGNS_REQUEST, _MAX_RETRIES + 1)


@patch("time.sleep", lambda _: None)
class TestMeErrorHandler(TestCase):
    @HttpMocker()
    def test_403_is_ignored(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_ME_REQUEST, HttpResponse(body="", status_code=403))

        output = _read("me")

        assert output.records == []
        assert output.errors == []
        http_mocker.assert_number_of_calls(_ME_REQUEST, 1)
