# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from requests_mock import ANY, Mocker

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_URL = "https://api.ads.openai.com/v1"
_CONFIG = {"api_key": "test-key", "start_date": "2026-09-01", "end_date": "2026-09-14"}
_TIME_RANGE = '{"type":"date_range","since":"2026-09-01","until":"2026-09-14"}'
_UNEXPECTED_REQUEST = {"status_code": 400, "json": {"error": {"message": "The test did not expect this request."}}}


@pytest.fixture(autouse=True)
def isolated_http(requests_mock: Mocker, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # The CDK caches parent-stream responses in a SQLite file. Keep that file out of `unit_tests/` and out of other tests.
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    # Registered first, so the mocks of each test take precedence. A request that no mock matches then
    # fails the read at once, which also stops a paginator that does not stop.
    requests_mock.register_uri(ANY, ANY, **_UNEXPECTED_REQUEST)


def _source(config: dict, state: list | None = None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state or StateBuilder().build(),
    )


def _read(stream: str, sync_mode: SyncMode = SyncMode.full_refresh, state: list | None = None, config: dict = _CONFIG) -> EntrypointOutput:
    output = read(_source(config, state), config, CatalogBuilder().with_stream(stream, sync_mode).build(), state)
    assert output.errors == []
    return output


def _records(output: EntrypointOutput) -> list:
    return [message.record.data for message in output.records]


def _page(rows: list[dict], has_more: bool = False) -> dict:
    ids = [row["id"] for row in rows]
    return {"object": "list", "data": rows, "first_id": ids[0] if ids else None, "last_id": ids[-1] if ids else None, "has_more": has_more}


def _mock_page(requests_mock: Mocker, path_and_query: str, *ids: str, has_more: bool = False) -> None:
    requests_mock.get(f"{_URL}{path_and_query}", complete_qs=True, json=_page([{"id": i} for i in ids], has_more))


def _mock_campaign_ad_group_ad(requests_mock: Mocker) -> None:
    _mock_page(requests_mock, "/campaigns?limit=500", "cmpn_1")
    _mock_page(requests_mock, "/ad_groups?limit=500&campaign_id=cmpn_1", "adgrp_1")
    _mock_page(requests_mock, "/ads?limit=500&ad_group_id=adgrp_1", "ad_1")


def _mock_insights(requests_mock: Mocker, *rows: dict) -> None:
    requests_mock.get(f"{_URL}/ad_account/insights", [{"json": {**_page(list(rows)), "count": len(rows)}}, _UNEXPECTED_REQUEST])


def _insights_query(requests_mock: Mocker) -> dict:
    [request] = [r for r in requests_mock.request_history if r.path == "/v1/ad_account/insights"]
    return parse_qs(urlsplit(request.url).query)


def test_discover_publishes_keys_schemas_and_cursors() -> None:
    streams = _source(_CONFIG).discover(logging.getLogger("airbyte"), _CONFIG).streams

    assert len(streams) == 19
    assert all(stream.source_defined_primary_key and stream.json_schema["properties"] for stream in streams)
    cursors = {stream.name: stream.default_cursor_field for stream in streams if SyncMode.incremental in stream.supported_sync_modes}
    assert len(cursors) == 11
    assert all(cursor == (["date"] if name.endswith("_conversions") else ["readable_time"]) for name, cursor in cursors.items())


def test_check_and_ad_account_read_the_root_object(requests_mock: Mocker) -> None:
    account = {"id": "act_1", "name": "Acme", "currency_code": "USD", "timezone": "America/Los_Angeles"}
    requests_mock.get(f"{_URL}/ad_account", json=account)

    status = _source(_CONFIG).check(logging.getLogger("airbyte"), _CONFIG)

    assert status.status == Status.SUCCEEDED
    assert _records(_read("ad_account")) == [account]
    assert all(request.headers["Authorization"] == "Bearer test-key" for request in requests_mock.request_history)


@pytest.mark.parametrize(
    "stream,path",
    [
        ("campaigns", "/campaigns"),
        ("conversion_event_settings", "/conversions/event_settings"),
        ("custom_audiences", "/custom_audiences"),
        ("conversion_pixels", "/conversions/pixels"),
    ],
)
def test_list_stream_follows_last_id_until_has_more_is_false(requests_mock: Mocker, stream: str, path: str) -> None:
    _mock_page(requests_mock, f"{path}?limit=500", "id_1", has_more=True)
    _mock_page(requests_mock, f"{path}?limit=500&after=id_1", "id_2")

    assert _records(_read(stream)) == [{"id": "id_1"}, {"id": "id_2"}]


def test_ad_groups_and_ads_are_read_per_parent_and_carry_the_parent_id(requests_mock: Mocker) -> None:
    _mock_campaign_ad_group_ad(requests_mock)

    assert _records(_read("ad_groups")) == [{"id": "adgrp_1", "campaign_id": "cmpn_1"}]
    assert _records(_read("ads")) == [{"id": "ad_1", "ad_group_id": "adgrp_1"}]


@pytest.mark.parametrize(
    "stream,aggregation_level,entity_id",
    [
        ("campaign_conversions", "campaign", "cmpn_1"),
        ("ad_group_conversions", "ad_group", "adgrp_1"),
        ("ad_conversions", "ad", "ad_1"),
    ],
)
def test_conversions_post_one_entity_and_keep_a_cursor_per_entity(
    requests_mock: Mocker, stream: str, aggregation_level: str, entity_id: str
) -> None:
    _mock_campaign_ad_group_ad(requests_mock)
    row = {"entity_id": entity_id, "date": "2026-09-13", "conversions": 3, "click_through_conversions": 2, "view_through_conversions": 1}
    requests_mock.post(f"{_URL}/conversions/insights", json={"object": "list", "data": [row], "count": 1, "account_currency": "USD"})

    output = _read(stream, SyncMode.incremental)

    assert _records(output) == [row]
    [post] = [request for request in requests_mock.request_history if request.method == "POST"]
    assert post.json() == {
        "aggregation_level": aggregation_level,
        "time_granularity": "daily",
        "entity_ids": [entity_id],
        "time_ranges": [_TIME_RANGE],
    }
    [partition_state] = output.most_recent_state.stream_state.states
    assert partition_state["partition"]["entity_id"] == entity_id
    assert partition_state["cursor"] == {"date": "2026-09-13"}


@pytest.mark.parametrize(
    "stream,aggregation_level,segment",
    [
        ("ad_account_insights", "ad_account", None),
        ("campaign_insights", "campaign", None),
        ("ad_group_insights", "ad_group", None),
        ("ad_insights", "ad", None),
        ("campaign_insights_by_country", "campaign", "country"),
        ("campaign_insights_by_device", "campaign", "device"),
        ("campaign_insights_by_platform", "campaign", "platform"),
        ("campaign_insights_by_product", "campaign", "product"),
    ],
)
def test_insights_request_one_date_range_and_save_the_cursor(
    requests_mock: Mocker, stream: str, aggregation_level: str, segment: str | None
) -> None:
    row = {"id": "ins_1", "start_time": 1789282800, "end_time": 1789369200, "readable_time": "2026-09-13"}
    _mock_insights(requests_mock, row)

    output = _read(stream, SyncMode.incremental)

    assert _records(output) == [row]
    query = _insights_query(requests_mock)
    assert query["time_granularity"] == ["daily"]
    assert query["aggregation_level"] == [aggregation_level]
    assert query.get("segments[]") == ([segment] if segment else None)
    assert query["time_ranges[]"] == [_TIME_RANGE]
    assert query["limit"] == ["2000"]
    assert "metadata.readable_time" in query["fields[]"]
    assert output.most_recent_state.stream_state.readable_time == "2026-09-13"


def test_incremental_insights_sync_reads_the_lookback_window_again(requests_mock: Mocker) -> None:
    _mock_insights(requests_mock)
    state = StateBuilder().with_stream_state("campaign_insights", {"readable_time": "2026-09-13"}).build()

    _read("campaign_insights", SyncMode.incremental, state, {**_CONFIG, "lookback_window": 3})

    assert _insights_query(requests_mock)["time_ranges[]"] == ['{"type":"date_range","since":"2026-09-10","until":"2026-09-14"}']


def test_spend_limit_windows_reads_data_and_skips_a_403(requests_mock: Mocker) -> None:
    window = {"window_id": "win_1", "start_date": "2026-09-01", "end_date": "2026-10-01", "amount_micros": 5000000, "status": "active"}
    forbidden = {"status_code": 403, "json": {"error": {"message": "Forbidden"}}}
    requests_mock.get(f"{_URL}/ad_account/spend_limit_windows", [{"json": {"data": [window]}}, forbidden])

    assert _records(_read("spend_limit_windows")) == [window]
    assert _records(_read("spend_limit_windows")) == []
