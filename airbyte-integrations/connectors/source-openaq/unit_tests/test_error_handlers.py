# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import patch

import pytest
import yaml

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import MANIFEST_PATH, get_source


_API_KEY = "test-api-key"
_COUNTRY_ID = 155
_LOCATION_ID = 2178
_SENSOR_ID = 3917
_CONFIG = {"api_key": _API_KEY, "country_ids": [_COUNTRY_ID]}
_BASE_URL = "https://api.openaq.org/v3"
_PAGE_PARAMS = {"page": "1", "limit": "1000"}

_LOCATIONS_REQUEST = HttpRequest(
    url=f"{_BASE_URL}/locations",
    query_params={**_PAGE_PARAMS, "countries_id": str(_COUNTRY_ID)},
    headers={"X-API-Key": _API_KEY},
)
_SENSORS_REQUEST = HttpRequest(
    url=f"{_BASE_URL}/locations/{_LOCATION_ID}/sensors",
    query_params=_PAGE_PARAMS,
    headers={"X-API-Key": _API_KEY},
)
_DAYS_REQUEST = HttpRequest(
    url=f"{_BASE_URL}/sensors/{_SENSOR_ID}/days",
    query_params=_PAGE_PARAMS,
    headers={"X-API-Key": _API_KEY},
)


def _results(*records: dict) -> HttpResponse:
    return HttpResponse(body=json.dumps({"results": list(records)}), status_code=200)


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(_CONFIG, catalog), _CONFIG, catalog, expecting_exception=expecting_exception)


@pytest.fixture(autouse=True)
def _skip_backoff_sleep():
    with patch("time.sleep", return_value=None):
        yield


def test_manifest_has_no_composite_error_handler() -> None:
    assert "CompositeErrorHandler" not in MANIFEST_PATH.read_text()


@pytest.mark.parametrize("stream_name", ["locations", "sensors", "measurements_daily"])
def test_stream_uses_default_error_handler(stream_name: str) -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    error_handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler["type"] == "DefaultErrorHandler"


@pytest.fixture
def http_mocker():
    with HttpMocker() as mocker:
        yield mocker


def test_locations_422_fails_with_config_error(http_mocker: HttpMocker) -> None:
    http_mocker.get(_LOCATIONS_REQUEST, HttpResponse(body=json.dumps({"detail": "invalid countries_id"}), status_code=422))

    output = _read("locations", expecting_exception=True)

    assert not output.records
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
    assert any("Use numeric OpenAQ country IDs" in error.trace.error.message for error in output.errors)
    http_mocker.assert_number_of_calls(_LOCATIONS_REQUEST, 1)


def test_locations_500_is_retried(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        _LOCATIONS_REQUEST,
        [HttpResponse(body="{}", status_code=500), _results({"id": _LOCATION_ID, "name": "Loc"})],
    )

    output = _read("locations")

    assert [record.record.data["id"] for record in output.records] == [_LOCATION_ID]
    assert not output.errors
    http_mocker.assert_number_of_calls(_LOCATIONS_REQUEST, 2)


def test_sensors_500_is_retried(http_mocker: HttpMocker) -> None:
    http_mocker.get(_LOCATIONS_REQUEST, _results({"id": _LOCATION_ID, "name": "Loc"}))
    http_mocker.get(
        _SENSORS_REQUEST,
        [HttpResponse(body="{}", status_code=500), _results({"id": _SENSOR_ID, "name": "pm25 µg/m³"})],
    )

    output = _read("sensors")

    assert [record.record.data["id"] for record in output.records] == [_SENSOR_ID]
    assert not output.errors
    http_mocker.assert_number_of_calls(_SENSORS_REQUEST, 2)


def test_measurements_daily_500_is_ignored(http_mocker: HttpMocker) -> None:
    http_mocker.get(_LOCATIONS_REQUEST, _results({"id": _LOCATION_ID, "name": "Loc"}))
    http_mocker.get(_SENSORS_REQUEST, _results({"id": _SENSOR_ID, "name": "pm25 µg/m³"}))
    http_mocker.get(_DAYS_REQUEST, HttpResponse(body=json.dumps({"detail": "Internal Server Error"}), status_code=500))

    output = _read("measurements_daily")

    assert not output.records
    assert not output.errors
    http_mocker.assert_number_of_calls(_DAYS_REQUEST, 1)
