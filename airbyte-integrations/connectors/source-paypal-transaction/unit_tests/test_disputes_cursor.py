# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import requests_mock
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_STREAM_NAME = "list_disputes"
_TOKEN_URL = "https://api-m.paypal.com/v1/oauth2/token"
_DISPUTES_URL = "https://api-m.paypal.com/v1/customer/disputes"
_DISPUTE_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
_PAYPAL_MAX_LOOKBACK = timedelta(days=180)
_INVALID_DATE_RANGE_RESPONSE = {
    "name": "INVALID_REQUEST",
    "message": "Request is not well-formed, syntactically incorrect, or violates schema.",
    "details": [
        {
            "field": "update_time_after",
            "value": "",
            "location": "query",
            "issue": "INVALID_DATE_RANGE",
            "description": "The date range is invalid.",
        }
    ],
}


def _parse_dispute_datetime(value: str) -> datetime:
    return datetime.strptime(value, _DISPUTE_DATE_FORMAT).replace(tzinfo=timezone.utc)


def _format_dispute_datetime(value: datetime) -> str:
    return value.strftime(_DISPUTE_DATE_FORMAT)[:23] + "Z"


def _resolve_start_datetime(config: Dict[str, Any]) -> datetime:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    start_datetime = manifest["definitions"]["streams"]["list_disputes"]["incremental_sync"]["start_datetime"]
    return MinMaxDatetime(
        datetime=start_datetime["datetime"],
        datetime_format=_DISPUTE_DATE_FORMAT,
        min_datetime=start_datetime.get("min_datetime", ""),
        parameters={},
    ).get_datetime(config=config)


# PayPal's customer-disputes API rejects update_time_after older than 180 days with
# INVALID_DATE_RANGE. The resolved start boundary is evaluated once at stream build time and
# reused for every request that follows, so it needs margin inside the window - landing exactly
# on 180 days means every request is already out of range by the time it is sent.
@pytest.mark.parametrize(
    "dispute_start_date_age",
    [
        pytest.param(None, id="default_start"),
        pytest.param(timedelta(days=180) - timedelta(seconds=5), id="user_start_seconds_inside_180_days"),
        pytest.param(timedelta(days=200), id="user_start_outside_180_days"),
    ],
)
def test_list_disputes_start_datetime_stays_inside_paypal_180_day_window(dispute_start_date_age: Optional[timedelta]) -> None:
    config: Dict[str, Any] = {}
    if dispute_start_date_age is not None:
        config["dispute_start_date"] = _format_dispute_datetime(datetime.now(timezone.utc) - dispute_start_date_age)

    age = datetime.now(timezone.utc) - _resolve_start_datetime(config)

    assert age <= timedelta(days=179, minutes=1), f"start boundary is {age} old, PayPal rejects anything past 180 days"


def test_list_disputes_recent_user_start_date_is_kept() -> None:
    dispute_start_date = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(days=30)

    resolved = _resolve_start_datetime({"dispute_start_date": _format_dispute_datetime(dispute_start_date)})

    assert resolved == dispute_start_date


def _paypal_disputes_callback(request, context) -> Dict[str, Any]:
    update_time_after = _parse_dispute_datetime(request.qs["update_time_after"][0].upper())
    if datetime.now(timezone.utc) - update_time_after > _PAYPAL_MAX_LOOKBACK:
        context.status_code = 400
        return _INVALID_DATE_RANGE_RESPONSE
    return {"items": []}


def _read_list_disputes(config: Dict[str, Any]):
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    source = YamlDeclarativeSource(config=config, catalog=catalog, state=None, path_to_yaml=str(_MANIFEST_PATH))
    return read(source, config, catalog, None, expecting_exception=True)


def test_list_disputes_first_sync_requests_stay_inside_paypal_180_day_window() -> None:
    config = {
        "client_id": "a-client-id",
        "client_secret": "a-client-secret",
        "start_date": "2024-01-01T00:00:00Z",
        "is_sandbox": False,
        "time_window": 31,
    }
    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, json={"access_token": "an-access-token", "expires_in": 3600})
        disputes_mock = mocker.get(_DISPUTES_URL, json=_paypal_disputes_callback)

        read_started_at = datetime.now(timezone.utc)
        output = _read_list_disputes(config)
        read_finished_at = datetime.now(timezone.utc)

    windows: List[Dict[str, str]] = sorted(
        ({key: values[0].upper() for key, values in request.qs.items()} for request in disputes_mock.request_history),
        key=lambda params: params["update_time_after"],
    )
    assert not output.errors, [error.trace.error.message for error in output.errors]
    assert len(windows) == 6
    first_start = _parse_dispute_datetime(windows[0]["update_time_after"])
    assert read_finished_at - first_start < _PAYPAL_MAX_LOOKBACK
    assert read_started_at - first_start >= timedelta(days=179) - timedelta(seconds=1)
    for previous, current in zip(windows, windows[1:]):
        previous_start = _parse_dispute_datetime(previous["update_time_after"])
        previous_end = _parse_dispute_datetime(previous["update_time_before"])
        assert previous_end == previous_start + timedelta(days=31) - timedelta(seconds=1)
        assert _parse_dispute_datetime(current["update_time_after"]) == previous_end + timedelta(seconds=1)
    for params in windows:
        assert set(params) == {"update_time_after", "update_time_before", "page_size"}
        assert params["page_size"] == "50"
