# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from requests_mock import ANY, Mocker

from airbyte_cdk.models import AirbyteStreamStatus, AirbyteStreamStatusReasonType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.http import rate_limiting
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_URL = "https://api.ads.openai.com/v1"
_CONFIG = {"api_key": "test-key", "start_date": "2026-09-01", "end_date": "2026-09-14"}
_UNEXPECTED_REQUEST = {"status_code": 400, "json": {"error": {"message": "The test did not expect this request."}}}
_PIXELS_URL = f"{_URL}/conversions/pixels"
# A 429 without this header empties the connector's 600 calls per minute budget until the minute is over.
# The header keeps that budget out of the tests, which check the retry schedule of the error handlers.
_TOO_MANY_REQUESTS = {
    "status_code": 429,
    "headers": {"ratelimit-remaining": "599"},
    "json": {"error": {"message": "Rate limit exceeded"}},
}
_PIXEL_PAGE = {"object": "list", "data": [{"id": "px_1"}], "first_id": "px_1", "last_id": "px_1", "has_more": False}


@pytest.fixture(autouse=True)
def isolated_http(requests_mock: Mocker, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # The CDK caches parent-stream responses in a SQLite file. Keep that file out of `unit_tests/` and out of other tests.
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    requests_mock.register_uri(ANY, ANY, **_UNEXPECTED_REQUEST)


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    waits: list[float] = []
    monkeypatch.setattr(rate_limiting, "time", SimpleNamespace(sleep=waits.append))
    return waits


def _read(stream: str) -> EntrypointOutput:
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH), catalog=CatalogBuilder().build(), config=_CONFIG, state=StateBuilder().build()
    )
    return read(source, _CONFIG, CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build())


def _rate_limited_statuses(printed: str, stream: str) -> int:
    # The CDK prints the RATE_LIMITED stream status straight to stdout instead of passing it to the entrypoint.
    statuses = [json.loads(line)["trace"]["stream_status"] for line in printed.splitlines() if '"stream_status"' in line]
    return sum(
        1
        for status in statuses
        if status["stream_descriptor"]["name"] == stream
        and any(reason["type"] == AirbyteStreamStatusReasonType.RATE_LIMITED.value for reason in status.get("reasons") or [])
    )


def test_conversion_pixels_skips_a_404_when_pixel_management_is_not_enabled(requests_mock: Mocker) -> None:
    requests_mock.get(_PIXELS_URL, status_code=404, json={"error": {"message": "Not found"}})

    output = _read("conversion_pixels")

    assert output.errors == []
    assert output.records == []
    assert output.get_stream_statuses("conversion_pixels")[-1] == AirbyteStreamStatus.COMPLETE
    assert output.is_in_logs("Pixel management is not enabled for this ad account")
    assert len(requests_mock.request_history) == 1


@pytest.mark.parametrize(
    "stream,url,page",
    [
        ("campaigns", f"{_URL}/campaigns", {**_PIXEL_PAGE, "data": [{"id": "cmpn_1"}], "first_id": "cmpn_1", "last_id": "cmpn_1"}),
        ("conversion_pixels", _PIXELS_URL, _PIXEL_PAGE),
        ("spend_limit_windows", f"{_URL}/ad_account/spend_limit_windows", {"data": [{"window_id": "win_1"}]}),
    ],
)
def test_a_429_is_reported_as_rate_limited_and_retried_on_the_same_schedule(
    requests_mock: Mocker, sleeps: list[float], capsys: pytest.CaptureFixture[str], stream: str, url: str, page: dict
) -> None:
    requests_mock.get(url, [_TOO_MANY_REQUESTS, _TOO_MANY_REQUESTS, {"json": page}])

    output = _read(stream)

    assert output.errors == []
    assert len(output.records) == 1
    assert len(requests_mock.request_history) == 3
    assert _rate_limited_statuses(capsys.readouterr().out, stream) == 2
    assert sleeps == [11, 21]


def test_a_retry_after_header_on_a_429_sets_the_wait(requests_mock: Mocker, sleeps: list[float]) -> None:
    too_many = {**_TOO_MANY_REQUESTS, "headers": {**_TOO_MANY_REQUESTS["headers"], "Retry-After": "7"}}
    requests_mock.get(_PIXELS_URL, [too_many, {"json": _PIXEL_PAGE}])

    output = _read("conversion_pixels")

    assert output.errors == []
    assert len(output.records) == 1
    assert sleeps == [8]


def test_conversion_pixels_retries_a_503(requests_mock: Mocker, sleeps: list[float]) -> None:
    requests_mock.get(_PIXELS_URL, [{"status_code": 503}, {"json": _PIXEL_PAGE}])

    output = _read("conversion_pixels")

    assert output.errors == []
    assert len(output.records) == 1
    assert len(requests_mock.request_history) == 2


def test_spend_limit_windows_403_message_names_billing_permission_and_prints_the_api_reason(requests_mock: Mocker) -> None:
    reason = "You do not have permission to manage billing for this ad account."
    requests_mock.get(f"{_URL}/ad_account/spend_limit_windows", status_code=403, json={"error": {"message": reason}})

    output = _read("spend_limit_windows")

    assert output.errors == []
    assert output.records == []
    assert output.is_in_logs(f"Skipping spend_limit_windows: the API answered 403 \\({reason}\\)")
    assert output.is_in_logs("postpaid invoice billing")
    assert output.is_in_logs("permission to manage billing")


@pytest.mark.parametrize(
    ("body", "expected_reason"),
    [
        pytest.param({"json": {"error": "Forbidden"}}, "Forbidden", id="error_is_a_string"),
        pytest.param({"json": {"error": {}}}, "no error message", id="error_without_message"),
        pytest.param({"json": []}, "no error message", id="body_is_a_list"),
        pytest.param({"text": "Forbidden"}, "no error message", id="body_is_not_json"),
    ],
)
def test_spend_limit_windows_403_is_skipped_whatever_the_error_body_shape(
    requests_mock: Mocker, body: dict[str, Any], expected_reason: str
) -> None:
    requests_mock.get(f"{_URL}/ad_account/spend_limit_windows", status_code=403, **body)

    output = _read("spend_limit_windows")

    assert output.errors == []
    assert output.records == []
    assert output.is_in_logs(f"Skipping spend_limit_windows: the API answered 403 \\({expected_reason}\\)")


def test_a_404_on_another_stream_still_fails_the_sync(requests_mock: Mocker) -> None:
    requests_mock.get(f"{_URL}/custom_audiences", status_code=404, json={"error": {"message": "Not found"}})

    output = _read("custom_audiences")

    assert output.errors
    assert output.get_stream_statuses("custom_audiences")[-1] == AirbyteStreamStatus.INCOMPLETE
