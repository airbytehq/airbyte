# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock as rm
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder

from .conftest import _YAML_FILE_PATH


def _load_manifest():
    with open(_YAML_FILE_PATH) as f:
        return yaml.safe_load(f)


def test_daily_cursor_step_uses_config_interpolation():
    manifest = _load_manifest()
    cursor_def = manifest["definitions"]["report_daily_incremental_sync"]
    step = cursor_def["step"]
    assert "config.get('report_granularity'" in step, "report_daily_incremental_sync step should reference config.report_granularity"
    assert step.startswith("P"), "step should start with P (ISO 8601 duration prefix)"
    assert step.endswith("D"), "step should end with D (days suffix)"


def test_hourly_cursor_step_is_fixed_p1d():
    manifest = _load_manifest()
    cursor_def = manifest["definitions"]["report_hourly_incremental_sync"]
    assert cursor_def["step"] == "P1D"


def test_spec_includes_report_granularity_field():
    manifest = _load_manifest()
    spec_props = manifest["spec"]["connection_specification"]["properties"]
    assert "report_granularity" in spec_props
    field = spec_props["report_granularity"]
    assert field["default"] == 30
    assert field["type"] == "integer"
    assert field["minimum"] == 1
    assert field["maximum"] == 30


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("ads_reports_daily_stream", id="ads_reports_daily"),
        pytest.param("ads_reports_by_country_daily_stream", id="ads_reports_by_country_daily"),
        pytest.param("ad_groups_reports_daily_stream", id="ad_groups_reports_daily"),
        pytest.param("campaigns_reports_daily_stream", id="campaigns_reports_daily"),
        pytest.param("advertisers_reports_daily_stream", id="advertisers_reports_daily"),
    ],
)
def test_daily_streams_do_not_override_cursor(stream_name):
    manifest = _load_manifest()
    stream_def = manifest["definitions"][stream_name]
    assert (
        "incremental_sync" not in stream_def
    ), f"{stream_name} should not override incremental_sync (all daily streams inherit the configurable cursor)"


@pytest.mark.parametrize(
    "report_granularity,max_days",
    [
        pytest.param(1, 2, id="1_day_step"),
        pytest.param(30, 31, id="30_day_step_default"),
    ],
)
def test_ads_reports_daily_respects_configured_step(report_granularity, max_days):
    config = {
        "access_token": "TOKEN",
        "start_date": "2024-01-01",
        "end_date": "2024-01-05",
        "report_granularity": report_granularity,
        "environment": {"advertiser_id": "12345"},
    }

    catalog = CatalogBuilder().with_stream("ads_reports_daily", SyncMode.incremental).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=[])

    with rm.Mocker() as m:
        m.get(
            "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
            json={
                "code": 0,
                "message": "ok",
                "data": {
                    "list": [],
                    "page_info": {"page": 1, "page_size": 1000, "total_page": 1, "total_number": 0},
                },
            },
        )
        list(source.read(logger=None, config=config, catalog=catalog, state=[]))

        report_requests = [h for h in m.request_history if "report/integrated/get" in h.path]
        assert len(report_requests) > 0, "Expected at least one report API request"

        for req in report_requests:
            params = parse_qs(urlparse(req.url).query)
            start = params.get("start_date", [None])[0]
            end = params.get("end_date", [None])[0]
            if start and end:
                start_dt = datetime.strptime(start, "%Y-%m-%d")
                end_dt = datetime.strptime(end, "%Y-%m-%d")
                delta = (end_dt - start_dt).days
                assert (
                    delta <= max_days
                ), f"Date range {start} to {end} spans {delta} days; expected <={max_days} with report_granularity={report_granularity}"


def test_error_40067_handler_is_config_error_on_daily_report_handler():
    manifest = _load_manifest()
    handler_def = manifest["definitions"]["report_daily_error_handler"]
    filters = handler_def["response_filters"]
    error_40067_filters = [f for f in filters if "40067" in f.get("predicate", "")]
    assert len(error_40067_filters) == 1, "Expected exactly one error handler for code 40067"
    handler = error_40067_filters[0]
    assert handler["action"] == "FAIL"
    assert handler.get("failure_type") == "config_error", "Error 40067 should be a config_error"
    assert (
        "daily reports date step" in handler["error_message"].lower()
    ), "Error message should guide user to reduce the Daily Reports Date Step setting"


def test_error_40067_not_on_global_requester():
    manifest = _load_manifest()
    global_filters = manifest["definitions"]["requester"]["error_handler"]["response_filters"]
    error_40067 = [f for f in global_filters if "40067" in f.get("predicate", "")]
    assert len(error_40067) == 0, "Error 40067 config_error should NOT be on the global requester"


RETRY_ERROR_MESSAGES = {
    "60001": "TikTok Marketing API is under service maintenance (error 60001).",
    "50000": "TikTok Marketing API returned a server-side error (code 50000).",
    "51041": "TikTok Marketing API returned a server-side error (code 51041).",
    "51004": "TikTok Marketing API returned a server-side error (code 51004).",
}
RETRY_ERROR_HANDLER_LOCATIONS = {
    "global": lambda manifest: manifest["definitions"]["requester"]["error_handler"]["response_filters"],
    "daily_report": lambda manifest: manifest["definitions"]["report_daily_error_handler"]["response_filters"],
    "pixel_instant_page_events": lambda manifest: manifest["definitions"]["pixel_instant_page_events"]["retriever"]["requester"][
        "error_handler"
    ]["response_filters"],
    "pixel_events_statistics": lambda manifest: manifest["definitions"]["pixel_events_statistics"]["retriever"]["requester"][
        "error_handler"
    ]["response_filters"],
}
BANNED_RETRY_MESSAGE_PHRASES = (
    "{{",
    "the connector will retry automatically",
    "you may need to re-sync",
)


@pytest.mark.parametrize("code,expected_message", RETRY_ERROR_MESSAGES.items())
@pytest.mark.parametrize("location", RETRY_ERROR_HANDLER_LOCATIONS)
def test_transient_retry_error_filters_have_stable_messages(location, code, expected_message):
    manifest = _load_manifest()
    filters = RETRY_ERROR_HANDLER_LOCATIONS[location](manifest)
    matching_filters = [f for f in filters if f"code') == {code}" in f.get("predicate", "")]
    assert len(matching_filters) == 1, f"Expected one handler for code {code} in {location}"
    handler = matching_filters[0]
    assert handler["action"] == "RETRY"
    assert handler["failure_type"] == "transient_error"
    assert handler["error_message"] == expected_message
    assert not any(phrase in handler["error_message"].lower() for phrase in BANNED_RETRY_MESSAGE_PHRASES)


@pytest.mark.parametrize("code,expected_message", RETRY_ERROR_MESSAGES.items())
def test_transient_retry_error_messages_match_across_handlers(code, expected_message):
    manifest = _load_manifest()
    messages = []
    for location, get_filters in RETRY_ERROR_HANDLER_LOCATIONS.items():
        matching_filters = [f for f in get_filters(manifest) if f"code') == {code}" in f.get("predicate", "")]
        assert len(matching_filters) == 1, f"Expected one handler for code {code} in {location}"
        messages.append(matching_filters[0]["error_message"])
    assert messages == [expected_message] * len(RETRY_ERROR_HANDLER_LOCATIONS)


@pytest.mark.parametrize(
    "retriever_name",
    [
        pytest.param("base_report_retriever", id="basic_daily_retriever"),
        pytest.param("audience_base_report_retriever", id="audience_daily_retriever"),
    ],
)
def test_daily_retrievers_use_report_daily_error_handler(retriever_name):
    manifest = _load_manifest()
    retriever = manifest["definitions"][retriever_name]
    requester = retriever["requester"]
    assert "error_handler" in requester, f"{retriever_name} requester should override error_handler"
    assert requester["error_handler"]["$ref"] == "#/definitions/report_daily_error_handler"
