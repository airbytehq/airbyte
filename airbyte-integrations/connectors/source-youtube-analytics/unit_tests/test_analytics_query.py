# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Exercise the historical query stream through the real manifest and CDK read path."""

import logging
import time
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

import pytest
import requests_mock
import yaml
from _helpers import get_source
from components import AnalyticsQueryExtractor
from freezegun import freeze_time

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_API = "https://youtubeanalytics.googleapis.com/v2/reports"
_TOKEN = "https://oauth2.googleapis.com/token"
_STREAM = "analytics_channel_daily"


@pytest.fixture
def query_config(config):
    return {**config, "query_reports": {"channel_id": "owned-channel", "start_date": "2025-04-17", "end_date": "2025-04-19"}}


@pytest.fixture(autouse=True)
def no_wait(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)


def _table(days, reverse_headers=False):
    columns = {"day": "STRING", **AnalyticsQueryExtractor.METRICS}
    if reverse_headers:
        columns = dict(reversed(columns.items()))
    return {
        "columnHeaders": [
            {"name": name, "dataType": data_type, "columnType": "DIMENSION" if name == "day" else "METRIC"}
            for name, data_type in columns.items()
        ],
        "rows": [[day if name == "day" else 12.5 if data_type == "FLOAT" else 3 for name, data_type in columns.items()] for day in days],
    }


def _read(config, state=None, source=None, mode=SyncMode.incremental):
    catalog = CatalogBuilder().with_stream(_STREAM, mode).build()
    return read(source or get_source(config, state), config, catalog, state=state)


def _token(mocker):
    mocker.post(_TOKEN, json={"access_token": "token", "expires_in": 3600})


def _small_page_source(config, tmp_path, state=None):
    # A channel/day slice normally fits on one page. Lower only the page size to exercise
    # the manifest's pagination and failed-page recovery with realistic unique daily rows.
    manifest = yaml.safe_load((Path(__file__).parent.parent / "manifest.yaml").read_text())
    manifest["definitions"]["streams"][_STREAM]["retriever"]["paginator"]["pagination_strategy"]["page_size"] = 2
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(manifest))
    return YamlDeclarativeSource(path_to_yaml=str(path), config=config, state=state)


def test_query_stream_is_opt_in_and_existing_catalog_is_unchanged(config, query_config):
    old_names = {stream.name for stream in get_source(config).discover(logging.getLogger("test"), config).streams}
    catalog = get_source(query_config).discover(logging.getLogger("test"), query_config)
    assert {stream.name for stream in catalog.streams} == old_names | {_STREAM}
    stream = next(stream for stream in catalog.streams if stream.name == _STREAM)
    assert stream.source_defined_primary_key == [["channel_id"], ["day"]]
    assert stream.default_cursor_field == ["day"]


@freeze_time("2026-11-03")
@pytest.mark.parametrize("mode", [SyncMode.incremental, SyncMode.full_refresh])
def test_historical_query_uses_owner_channel_dates_and_emits_named_typed_records(query_config, mode):
    with requests_mock.Mocker() as mocker:
        _token(mocker)
        query = mocker.get(_API, json=_table(["2025-04-17", "2025-04-19"], reverse_headers=True))
        output = _read(query_config, mode=mode)
    assert output.errors == []
    assert len(output.records) == 2
    record = output.records[0].record.data
    assert record["channel_id"] == "owned-channel"
    assert record["day"] == "2025-04-17"
    assert record["views"] == 3 and type(record["views"]) is int
    assert record["averageViewDuration"] == 12.5
    assert record["engagedViews"] == 3
    params = query.last_request.qs
    assert params["ids"] == ["channel==owned-channel"]
    assert params["dimensions"] == ["day"]
    assert params["sort"] == ["day"]
    assert params["startdate"] == ["2025-04-17"]
    assert params["enddate"] == ["2025-04-19"]
    assert params["startindex"] == ["1"] and params["maxresults"] == ["200"]
    assert set(params["metrics"][0].split(",")) == {name.lower() for name in AnalyticsQueryExtractor.METRICS}
    assert not any("youtubereporting" in request.url for request in mocker.request_history)


@freeze_time("2026-11-03")
def test_pagination_is_one_based_and_resets_for_each_date_slice(query_config, tmp_path):
    query_config["query_reports"]["end_date"] = "2025-05-18"
    seen = []

    def page(request, context):
        start, end = request.qs["startdate"][0], request.qs["enddate"][0]
        index = int(request.qs["startindex"][0])
        seen.append((start, end, index))
        days = [start, (date.fromisoformat(start) + timedelta(days=1)).isoformat()]
        return _table(days if index == 1 else [])

    with requests_mock.Mocker() as mocker:
        _token(mocker)
        mocker.get(_API, json=page)
        output = _read(query_config, source=_small_page_source(query_config, tmp_path))
    assert output.errors == []
    assert sorted(seen) == sorted(
        [("2025-04-17", "2025-05-16", 1), ("2025-04-17", "2025-05-16", 3), ("2025-05-17", "2025-05-18", 1), ("2025-05-17", "2025-05-18", 3)]
    )
    assert len(output.records) == 4


@freeze_time("2026-11-03")
def test_resume_replays_lookback_and_bounds_end_by_lag(query_config):
    query_config["query_reports"].update({"start_date": "2026-10-01", "end_date": "2026-12-31", "lookback_days": 7})
    state = StateBuilder().with_stream_state(_STREAM, {"day": "2026-10-25"}).build()
    with requests_mock.Mocker() as mocker:
        _token(mocker)
        query = mocker.get(_API, json=_table(["2026-10-25", "2026-10-31"]))
        output = _read(query_config, state=state)
    assert output.errors == []
    assert query.last_request.qs["startdate"] == ["2026-10-18"]
    assert query.last_request.qs["enddate"] == ["2026-10-31"]
    assert output.most_recent_state.stream_state.day == "2026-10-31"


@freeze_time("2026-11-03")
def test_failed_second_page_does_not_checkpoint_the_incomplete_window(query_config, tmp_path):
    with requests_mock.Mocker() as mocker:
        _token(mocker)
        mocker.get(
            _API,
            [
                {"json": _table(["2025-04-17", "2025-04-18"])},
                {"status_code": 400, "json": {"error": {"code": 400, "message": "bad query"}}},
            ],
        )
        output = _read(query_config, source=_small_page_source(query_config, tmp_path))
    assert output.errors
    # The CDK may checkpoint the initial boundary, but must not advance into the failed slice.
    assert output.most_recent_state.stream_state.day == "2025-04-17"
    state = StateBuilder().with_stream_state(_STREAM, {"day": output.most_recent_state.stream_state.day}).build()
    with requests_mock.Mocker() as mocker:
        _token(mocker)
        query = mocker.get(_API, [{"json": _table(["2025-04-17", "2025-04-18"])}, {"json": _table(["2025-04-19"])}])
        resumed = _read(query_config, state=state, source=_small_page_source(query_config, tmp_path, state))
    assert resumed.errors == []
    assert [record.record.data["day"] for record in resumed.records] == ["2025-04-17", "2025-04-18", "2025-04-19"]
    assert [request.qs["startindex"] for request in query.request_history] == [["1"], ["3"]]


@freeze_time("2026-11-03")
def test_empty_historical_response_is_valid_and_does_not_invent_zero_records(query_config):
    table = _table([])
    del table["rows"]
    with requests_mock.Mocker() as mocker:
        _token(mocker)
        mocker.get(_API, json=table)
        output = _read(query_config)
    assert output.errors == [] and output.records == []


@freeze_time("2026-11-03")
def test_integer_headers_for_watch_time_and_duration_and_nullable_metrics_are_supported(query_config):
    body = _table(["2025-04-17"])
    for name in ("estimatedMinutesWatched", "averageViewDuration"):
        index = next(index for index, header in enumerate(body["columnHeaders"]) if header["name"] == name)
        body["columnHeaders"][index]["dataType"] = "INTEGER"
        body["rows"][0][index] = 42
    body["rows"][0][next(index for index, header in enumerate(body["columnHeaders"]) if header["name"] == "likes")] = None
    with requests_mock.Mocker() as mocker:
        _token(mocker)
        mocker.get(_API, json=body)
        output = _read(query_config)
    assert output.errors == []
    assert output.records[0].record.data["estimatedMinutesWatched"] == 42
    assert output.records[0].record.data["averageViewDuration"] == 42
    # The CDK may omit null fields; neither omission nor null may become a measured zero.
    assert output.records[0].record.data.get("likes") is None


@freeze_time("2026-11-03")
def test_query_without_end_date_uses_configured_lag(query_config):
    query_config["query_reports"].update({"start_date": "2026-10-29", "data_lag_days": 4})
    del query_config["query_reports"]["end_date"]
    with requests_mock.Mocker() as mocker:
        _token(mocker)
        query = mocker.get(_API, json=_table(["2026-10-29", "2026-10-30"]))
        output = _read(query_config)
    assert output.errors == []
    assert query.last_request.qs["enddate"] == ["2026-10-30"]


@pytest.mark.parametrize(
    "update",
    [
        {"start_date": "2025-02-30"},
        {"start_date": "2025-4-17"},
        {"end_date": "2025-04-16"},
        {"end_date": None},
        {"lookback_days": -1},
        {"data_lag_days": True},
        {"channel_id": " "},
    ],
)
def test_invalid_query_settings_fail_before_http(query_config, update):
    query_config["query_reports"].update(update)
    with pytest.raises((AirbyteTracedException, ValueError)):
        get_source(query_config).discover(logging.getLogger("test"), query_config)


def test_content_owner_query_configuration_is_rejected_explicitly(query_config):
    query_config["content_owner_id"] = "content-owner"
    with pytest.raises(AirbyteTracedException, match="channel owners only"):
        get_source(query_config).discover(logging.getLogger("test"), query_config)


@pytest.mark.parametrize("code", [400, 401, 403])
@freeze_time("2026-11-03")
def test_query_permission_or_parameter_errors_are_actionable(query_config, code):
    with requests_mock.Mocker() as mocker:
        _token(mocker)
        query = mocker.get(_API, status_code=code, json={"error": {"code": code, "message": "query denied"}})
        output = _read(query_config)
    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    assert "youtube.readonly" in output.errors[0].trace.error.message
    assert query.call_count == 1


@freeze_time("2026-11-03")
def test_transient_query_failure_is_retried(query_config):
    with requests_mock.Mocker() as mocker:
        _token(mocker)
        query = mocker.get(_API, [{"status_code": 503, "json": {"error": {"code": 503}}}, {"json": _table(["2025-04-17"])}])
        output = _read(query_config)
    assert output.errors == [] and len(output.records) == 1
    assert query.call_count == 2


@freeze_time("2026-11-03")
def test_daily_quota_exhaustion_is_not_retried_as_a_permission_error(query_config):
    with requests_mock.Mocker() as mocker:
        _token(mocker)
        query = mocker.get(
            _API,
            status_code=403,
            json={"error": {"code": 403, "message": "quota exhausted", "errors": [{"reason": "quotaExceeded"}]}},
        )
        output = _read(query_config)
    assert query.call_count == 1
    assert output.errors[0].trace.error.failure_type == FailureType.transient_error
    assert "quota is exhausted" in output.errors[0].trace.error.message


@pytest.mark.parametrize("defect", ["short_row", "duplicate_header", "wrong_type", "fractional_count", "out_of_bounds", "missing_header"])
@freeze_time("2026-11-03")
def test_malformed_query_responses_fail_instead_of_silently_losing_fields(query_config, defect):
    body = deepcopy(_table(["2025-04-17"]))
    if defect == "short_row":
        body["rows"][0].pop()
    elif defect == "duplicate_header":
        body["columnHeaders"][1] = body["columnHeaders"][0]
    elif defect == "wrong_type":
        body["columnHeaders"][1]["dataType"] = "STRING"
    elif defect == "fractional_count":
        body["rows"][0][1] = 3.5
    elif defect == "out_of_bounds":
        body["rows"][0][0] = "2025-04-16"
    else:
        body.pop("columnHeaders")
    with requests_mock.Mocker() as mocker:
        _token(mocker)
        mocker.get(_API, json=body)
        output = _read(query_config)
    assert output.errors and output.records == []
