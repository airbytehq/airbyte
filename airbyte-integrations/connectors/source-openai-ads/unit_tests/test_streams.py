# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
import yaml
from freezegun import freeze_time
from jsonschema import Draft7Validator
from requests_mock import ANY, Mocker

from airbyte_cdk.models import AirbyteStateMessageSerializer, Status, SyncMode
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit
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


def _undeclared_paths(record: object, schema: dict, path: str = "") -> list[str]:
    if isinstance(record, dict):
        properties = schema.get("properties", {})
        undeclared = []
        for key, value in record.items():
            field_path = f"{path}.{key}" if path else key
            if key not in properties:
                undeclared.append(field_path)
            else:
                undeclared.extend(_undeclared_paths(value, properties[key], field_path))
        return undeclared

    if isinstance(record, list):
        item_schema = schema.get("items")
        if item_schema is None:
            return [path]
        return [
            undeclared_path
            for index, item in enumerate(record)
            for undeclared_path in _undeclared_paths(item, item_schema, f"{path}[{index}]")
        ]

    return []


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


def _mock_empty_insights(requests_mock: Mocker) -> None:
    requests_mock.get(f"{_URL}/ad_account/insights", json={**_page([]), "count": 0})


def _insights_query(requests_mock: Mocker) -> dict:
    [request] = [r for r in requests_mock.request_history if r.path == "/v1/ad_account/insights"]
    return parse_qs(urlsplit(request.url).query)


@pytest.mark.parametrize(
    ("config", "expected_workers"),
    [
        pytest.param({"num_workers": 1}, 2, id="one_worker_runs_two"),
        pytest.param({}, 3, id="default"),
    ],
)
def test_read_runs_with_at_least_two_workers(
    requests_mock: Mocker, monkeypatch: pytest.MonkeyPatch, config: dict, expected_workers: int
) -> None:
    _mock_campaign_ad_group_ad(requests_mock)
    worker_counts = []
    original_create = ConcurrentSource.create

    def create_spy(num_workers: int, *args, **kwargs):
        worker_counts.append(num_workers)
        return original_create(num_workers, *args, **kwargs)

    monkeypatch.setattr(ConcurrentSource, "create", staticmethod(create_spy))

    output = _read("ads", config={**_CONFIG, **config})

    assert output.errors == []
    assert _records(output) == [{"id": "ad_1", "ad_group_id": "adgrp_1"}]
    request_paths = {urlsplit(request.url).path for request in requests_mock.request_history}
    assert {"/v1/campaigns", "/v1/ad_groups", "/v1/ads"} <= request_paths
    assert worker_counts and all(count == expected_workers for count in worker_counts)


@pytest.mark.parametrize(
    "stream",
    [
        pytest.param("ad_account", id="ad_account"),
        pytest.param("ad_groups", id="ad_groups"),
        pytest.param("ads", id="ads"),
        pytest.param("campaigns", id="campaigns"),
    ],
)
def test_read_keeps_and_discover_declares_the_added_fields(requests_mock: Mocker, stream: str) -> None:
    added_fields = {
        "ad_account": {
            "creative_optimization_opt_in": True,
            "geographic_serving_country_code": "US",
            "geographic_serving_scope": "country",
            "review": {"reason": "approved", "screenshot_url": "https://example.com/account-review.png"},
            "account_integrity_review": {"review": {"reason": "verified", "screenshot_url": "https://example.com/integrity-review.png"}},
        },
        "ad_groups": {"hide_product_prices": False},
        "ads": {"review": {"reason": "approved", "screenshot_url": "https://example.com/ad-review.png"}},
        "campaigns": {"conversion_event_settings_automatically_attached": True},
    }
    record_ids = {"ad_account": "act_1", "ad_groups": "adgrp_1", "ads": "ad_1", "campaigns": "cmpn_1"}
    record = {"id": record_ids[stream], **added_fields[stream]}

    if stream == "ad_account":
        requests_mock.get(f"{_URL}/ad_account", json=record)
    elif stream == "ad_groups":
        _mock_page(requests_mock, "/campaigns?limit=500", "cmpn_1")
        requests_mock.get(
            f"{_URL}/ad_groups?limit=500&campaign_id=cmpn_1",
            complete_qs=True,
            json=_page([record]),
        )
    elif stream == "ads":
        _mock_page(requests_mock, "/campaigns?limit=500", "cmpn_1")
        _mock_page(requests_mock, "/ad_groups?limit=500&campaign_id=cmpn_1", "adgrp_1")
        requests_mock.get(
            f"{_URL}/ads?limit=500&ad_group_id=adgrp_1",
            complete_qs=True,
            json=_page([record]),
        )
    else:
        requests_mock.get(f"{_URL}/campaigns?limit=500", complete_qs=True, json=_page([record]))

    output = _read(stream)

    assert output.errors == []
    [emitted_record] = _records(output)
    expected_record = dict(record)
    if stream == "ad_groups":
        expected_record["campaign_id"] = "cmpn_1"
    elif stream == "ads":
        expected_record["ad_group_id"] = "adgrp_1"
    assert emitted_record == expected_record

    streams = {item.name: item for item in _source(_CONFIG).discover(logging.getLogger("airbyte"), _CONFIG).streams}
    schema = streams[stream].json_schema
    assert _undeclared_paths(emitted_record, schema) == []
    assert list(Draft7Validator(schema).iter_errors(emitted_record)) == []


def test_discover_publishes_keys_schemas_and_cursors() -> None:
    streams = _source(_CONFIG).discover(logging.getLogger("airbyte"), _CONFIG).streams

    assert len(streams) == 19
    assert all(stream.source_defined_primary_key and stream.json_schema["properties"] for stream in streams)
    cursors = {stream.name: stream.default_cursor_field for stream in streams if SyncMode.incremental in stream.supported_sync_modes}
    assert len(cursors) == 11
    assert all(cursor == (["date"] if name.endswith("_conversions") else ["readable_time"]) for name, cursor in cursors.items())


@pytest.mark.parametrize(
    ("saved", "migrated"),
    [
        ({"lookback_window": 0, "num_workers": 1}, {"lookback_window": 1, "num_workers": 2}),
        ({"lookback_window": 1, "num_workers": 2}, {"lookback_window": 1, "num_workers": 2}),
        ({"lookback_window": 32, "num_workers": 5}, {"lookback_window": 32, "num_workers": 5}),
        ({}, {}),
    ],
)
def test_saved_config_below_the_spec_minimums_is_raised_to_them(saved: dict, migrated: dict, tmp_path: Path) -> None:
    config = {**_CONFIG, **saved}
    source = _source(config)
    spec = source.spec(logging.getLogger("airbyte")).connectionSpecification

    assert spec["properties"]["lookback_window"]["minimum"] == 1
    assert spec["properties"]["num_workers"]["minimum"] == 2
    assert source.configure(config, str(tmp_path)) == {**_CONFIG, **migrated}
    check_config_against_spec_or_exit(source.configure(config, str(tmp_path)), source.spec(logging.getLogger("airbyte")))


def test_discover_declares_documented_custom_audience_and_ad_account_fields() -> None:
    streams = {stream.name: stream for stream in _source(_CONFIG).discover(logging.getLogger("airbyte"), _CONFIG).streams}

    assert set(streams["custom_audiences"].json_schema["properties"]) == {
        "id",
        "created_at",
        "updated_at",
        "name",
        "description",
        "status",
        "hash_spec_version",
        "uploaded_identifier_count_range",
        "matched_identifier_count_range",
        "matched_user_count_range",
        "invalid_identifier_count_range",
        "membership_revision",
    }
    assert {"legal_name", "account_name", "brand_name"} <= set(streams["ad_account"].json_schema["properties"])


def test_discover_types_documented_nested_fields() -> None:
    streams = {stream.name: stream for stream in _source(_CONFIG).discover(logging.getLogger("airbyte"), _CONFIG).streams}

    ad_group_properties = streams["ad_groups"].json_schema["properties"]
    assert set(ad_group_properties["bidding_config"]["properties"]["custom_audience_bid_multipliers"]["items"]["properties"]) == {
        "custom_audience_id",
        "bid_multiplier_micros",
    }
    assert set(ad_group_properties["product_set"]["properties"]["filters"]["items"]["properties"]) == {
        "field",
        "operator",
        "values",
    }
    assert set(streams["conversion_event_settings"].json_schema["properties"]["campaigns"]["items"]["properties"]) == {
        "id",
        "name",
    }
    for stream_name in ("campaigns", "ad_groups", "ads"):
        assert set(streams[stream_name].json_schema["properties"]["landing_page_configuration"]["properties"]) == {"query_string_template"}


def test_check_and_ad_account_read_the_root_object(requests_mock: Mocker) -> None:
    account = {
        "id": "act_1",
        "name": "Acme",
        "legal_name": "Acme Corporation",
        "account_name": "Acme Ads",
        "brand_name": "Acme",
        "currency_code": "USD",
        "timezone": "America/Los_Angeles",
    }
    requests_mock.get(f"{_URL}/ad_account", json=account)

    status = _source(_CONFIG).check(logging.getLogger("airbyte"), _CONFIG)
    streams = {stream.name: stream for stream in _source(_CONFIG).discover(logging.getLogger("airbyte"), _CONFIG).streams}

    assert status.status == Status.SUCCEEDED
    assert _records(_read("ad_account")) == [account]
    assert set(account) <= set(streams["ad_account"].json_schema["properties"])
    assert all(request.headers["Authorization"] == "Bearer test-key" for request in requests_mock.request_history)


def test_custom_audiences_read_keeps_documented_fields(requests_mock: Mocker) -> None:
    audience = {
        "id": "aud_1",
        "created_at": 1780000000,
        "updated_at": 1780003600,
        "name": "Acme customers",
        "description": None,
        "status": "ready",
        "hash_spec_version": "sha256",
        "uploaded_identifier_count_range": "1000-5000",
        "matched_identifier_count_range": "1000-5000",
        "matched_user_count_range": "500-1000",
        "invalid_identifier_count_range": "0-100",
        "membership_revision": 7,
    }
    requests_mock.get(f"{_URL}/custom_audiences?limit=500", complete_qs=True, json=_page([audience]))
    streams = {stream.name: stream for stream in _source(_CONFIG).discover(logging.getLogger("airbyte"), _CONFIG).streams}
    properties = set(streams["custom_audiences"].json_schema["properties"])

    [record] = _records(_read("custom_audiences"))
    assert record == {key: value for key, value in audience.items() if key != "description"}
    assert set(record) == properties - {"description"}
    # The Airbyte protocol serializer omits null values from record data.
    normalized_record = {**record, "description": None}

    assert normalized_record == audience
    assert set(normalized_record) == properties
    if Draft7Validator is not None:
        Draft7Validator(streams["custom_audiences"].json_schema).validate(audience)
        Draft7Validator(streams["custom_audiences"].json_schema).validate(record)


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
def test_conversions_post_the_entity_group_and_save_one_cursor(
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
        "attribution_time_basis": "ad_event_time",
        "attribution_window_days": 30,
        "view_through_attribution_window_days": 1,
        "entity_ids": [entity_id],
        "time_ranges": [_TIME_RANGE],
    }
    stream_state = output.most_recent_state.stream_state
    assert stream_state.use_global_cursor is True
    assert stream_state.state == {"date": "2026-09-13"}
    assert "states" not in stream_state.__dict__


@freeze_time("2026-09-30T18:00:00Z")
def test_conversions_post_up_to_100_entities_per_request_and_date_slice(requests_mock: Mocker) -> None:
    campaign_ids = [f"cmpn_{index:03}" for index in range(150)]
    _mock_page(requests_mock, "/campaigns?limit=500", *campaign_ids)
    requests_mock.post(f"{_URL}/conversions/insights", json={"object": "list", "data": [], "count": 0, "account_currency": "USD"})
    config = {**_CONFIG, "end_date": "2026-09-20"}

    _read("campaign_conversions", SyncMode.incremental, config=config)

    def body(entity_ids: list[str], since: str, until: str) -> dict:
        return {
            "aggregation_level": "campaign",
            "time_granularity": "daily",
            "attribution_time_basis": "ad_event_time",
            "attribution_window_days": 30,
            "view_through_attribution_window_days": 1,
            "entity_ids": entity_ids,
            "time_ranges": [f'{{"type":"date_range","since":"{since}","until":"{until}"}}'],
        }

    actual = sorted(
        (request.json() for request in requests_mock.request_history if request.method == "POST"),
        key=lambda request_body: (request_body["entity_ids"][0], request_body["time_ranges"][0]),
    )
    assert actual == [
        body(campaign_ids[:100], "2026-09-01", "2026-09-14"),
        body(campaign_ids[:100], "2026-09-15", "2026-09-20"),
        body(campaign_ids[100:], "2026-09-01", "2026-09-14"),
        body(campaign_ids[100:], "2026-09-15", "2026-09-20"),
    ]


def _state_written_by_0_1_x(entity_ids: tuple[str, ...], with_global_state: bool = True) -> dict:
    state = {
        "use_global_cursor": False,
        "states": [
            {"partition": {"entity_id": entity_id, "parent_slice": {}}, "cursor": {"date": date}}
            for entity_id, date in zip(entity_ids, ("2026-09-10", "2026-09-06"))
        ],
        "lookback_window": 1,
        "parent_state": {},
    }
    if with_global_state:
        state["state"] = {"date": "2026-09-10"}
    return state


@pytest.mark.parametrize(
    "stream,entity_ids",
    [
        ("campaign_conversions", ("cmpn_1",)),
        ("ad_group_conversions", ("adgrp_1",)),
        ("ad_conversions", ("ad_1",)),
    ],
)
@pytest.mark.parametrize("with_global_state", [True, False])
def test_conversions_resume_from_0_1_x_per_entity_state_with_one_cursor(
    requests_mock: Mocker, stream: str, entity_ids: tuple[str, ...], with_global_state: bool
) -> None:
    _mock_campaign_ad_group_ad(requests_mock)
    row = {"entity_id": entity_ids[0], "date": "2026-09-12", "conversions": 1}
    requests_mock.post(f"{_URL}/conversions/insights", json={"object": "list", "data": [row], "count": 1, "account_currency": "USD"})
    state = StateBuilder().with_stream_state(stream, _state_written_by_0_1_x(entity_ids + ("stale_1",), with_global_state)).build()
    config = {**_CONFIG, "lookback_window": 2}
    expected_since = "2026-09-07" if with_global_state else config["start_date"]

    output = _read(stream, SyncMode.incremental, state, config)

    assert _records(output) == [row]
    actual_bodies = [
        (request.json()["entity_ids"], request.json()["time_ranges"])
        for request in requests_mock.request_history
        if request.method == "POST"
    ]
    assert actual_bodies == [(list(entity_ids), [f'{{"type":"date_range","since":"{expected_since}","until":"2026-09-14"}}'])]
    stream_state = output.most_recent_state.stream_state.__dict__
    assert stream_state["use_global_cursor"] is True
    assert stream_state["state"] == {"date": "2026-09-12"}
    assert "states" not in stream_state


def test_conversions_state_migration_keeps_global_state_and_skips_new_state(components_module) -> None:
    migration = components_module.PerEntityToGlobalCursorStateMigration()
    new_state = {"use_global_cursor": True, "state": {"date": "2026-09-10"}, "lookback_window": 1}

    assert migration.should_migrate(new_state) is False
    assert migration.should_migrate({}) is False
    assert migration.migrate(_state_written_by_0_1_x(("cmpn_1", "cmpn_2"))) == {
        "use_global_cursor": True,
        "state": {"date": "2026-09-10"},
        "lookback_window": 1,
        "parent_state": {},
    }
    assert "state" not in migration.migrate(_state_written_by_0_1_x(("cmpn_1", "cmpn_2"), with_global_state=False))
    assert "state" not in migration.migrate({"use_global_cursor": False, "states": []})


@freeze_time("2026-09-15T06:00:00Z")
def test_0_1_11_manifest_reads_state_migrated_by_the_current_connector(requests_mock: Mocker) -> None:
    _mock_campaign_ad_group_ad(requests_mock)
    row = {"entity_id": "ad_1", "date": "2026-09-10", "conversions": 1}
    response = {"object": "list", "data": [row], "count": 1, "account_currency": "USD"}
    requests_mock.post(f"{_URL}/conversions/insights", [{"json": response}, {"json": response}])
    config = {**_CONFIG, "lookback_window": 2}
    old_state = StateBuilder().with_stream_state("ad_conversions", _state_written_by_0_1_x(("ad_1",))).build()

    migrated_output = _read("ad_conversions", SyncMode.incremental, old_state, config)
    migrated_stream_state = migrated_output.most_recent_state.stream_state.__dict__
    assert migrated_stream_state["use_global_cursor"] is True
    assert migrated_stream_state["state"] == {"date": "2026-09-10"}
    assert "states" not in migrated_stream_state

    rollback_state = StateBuilder().with_stream_state("ad_conversions", migrated_stream_state).build()
    old_manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    for stream_name in ("campaign_conversions_stream", "ad_group_conversions_stream", "ad_conversions_stream"):
        stream = old_manifest["definitions"][stream_name]
        stream["retriever"]["partition_router"] = stream["retriever"]["partition_router"]["underlying_partition_router"]
        del stream["state_migrations"]
    old_manifest["definitions"]["conversions_requester"]["request_body_json"]["entity_ids"] = '{{ [ stream_slice["entity_id"] ] }}'
    old_source = ConcurrentDeclarativeSource(
        source_config=old_manifest,
        catalog=CatalogBuilder().build(),
        config=config,
        state=rollback_state,
    )
    rollback_output = read(old_source, config, CatalogBuilder().with_stream("ad_conversions", SyncMode.incremental).build(), rollback_state)

    assert rollback_output.errors == []
    post_requests = [request for request in requests_mock.request_history if request.method == "POST"]
    assert len(post_requests) == 2
    assert post_requests[1].json()["entity_ids"] == ["ad_1"]
    assert post_requests[1].json()["time_ranges"] == ['{"type":"date_range","since":"2026-09-08","until":"2026-09-14"}']


def test_nested_parent_streams_reuse_cached_campaigns_and_ad_groups(requests_mock: Mocker) -> None:
    campaign_ids = ("cmpn_1", "cmpn_2")
    ad_group_ids = {
        "cmpn_1": ("adgrp_11", "adgrp_12"),
        "cmpn_2": ("adgrp_21", "adgrp_22"),
    }
    _mock_page(requests_mock, "/campaigns?limit=500", *campaign_ids)
    for campaign_id, ids in ad_group_ids.items():
        _mock_page(requests_mock, f"/ad_groups?limit=500&campaign_id={campaign_id}", *ids)
        for ad_group_id in ids:
            _mock_page(requests_mock, f"/ads?limit=500&ad_group_id={ad_group_id}", f"ad_{ad_group_id}")
    requests_mock.post(
        f"{_URL}/conversions/insights",
        json={"object": "list", "data": [], "count": 0, "account_currency": "USD"},
    )

    config = _CONFIG
    catalog = (
        CatalogBuilder()
        .with_stream("ads", SyncMode.full_refresh)
        .with_stream("ad_group_conversions", SyncMode.incremental)
        .with_stream("ad_conversions", SyncMode.incremental)
        .build()
    )
    output = read(_source(config), config, catalog, StateBuilder().build())

    assert output.errors == []
    campaign_urls = [
        request.url
        for request in requests_mock.request_history
        if request.method == "GET" and urlsplit(request.url).path == "/v1/campaigns"
    ]
    ad_group_urls = [
        request.url
        for request in requests_mock.request_history
        if request.method == "GET" and urlsplit(request.url).path == "/v1/ad_groups"
    ]
    assert {
        "campaigns": Counter(campaign_urls),
        "ad_groups": Counter(ad_group_urls),
    } == {
        "campaigns": Counter({f"{_URL}/campaigns?limit=500": 1}),
        "ad_groups": Counter(
            {
                f"{_URL}/ad_groups?limit=500&campaign_id=cmpn_1": 1,
                f"{_URL}/ad_groups?limit=500&campaign_id=cmpn_2": 1,
            }
        ),
    }


_ABNORMAL_STATE = json.loads((Path(__file__).parent.parent / "integration_tests" / "abnormal_state.json").read_text())


@pytest.mark.parametrize("stream_state", _ABNORMAL_STATE, ids=lambda message: message["stream"]["stream_descriptor"]["name"])
def test_abnormal_state_requests_no_report_and_emits_state(requests_mock: Mocker, stream_state: dict) -> None:
    stream = stream_state["stream"]["stream_descriptor"]["name"]
    _mock_campaign_ad_group_ad(requests_mock)

    output = _read(stream, SyncMode.incremental, [AirbyteStateMessageSerializer.load(stream_state)])

    assert _records(output) == []
    assert not [request for request in requests_mock.request_history if request.path.endswith("/insights")]
    assert output.state_messages


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


@freeze_time("2026-09-15T06:00:00Z")
@pytest.mark.parametrize(
    "end_date,expected_end",
    [
        ("2026-12-31", "2026-09-14"),
        (None, "2026-09-14"),
        ("2026-09-10", "2026-09-10"),
    ],
    ids=["future-end-date-is-clamped", "default-end-date-uses-utc-minus-12", "past-end-date-is-honoured"],
)
def test_incremental_insights_end_date_controls_all_slices(requests_mock: Mocker, end_date: str | None, expected_end: str) -> None:
    _mock_empty_insights(requests_mock)
    config = {"api_key": "test-key", "start_date": "2026-08-25"}
    if end_date is not None:
        config["end_date"] = end_date

    _read("campaign_insights", SyncMode.incremental, config=config)

    actual_time_ranges = [
        value for request in requests_mock.request_history for value in parse_qs(urlsplit(request.url).query).get("time_ranges[]", [])
    ]
    assert sorted(actual_time_ranges) == sorted(
        [
            '{"type":"date_range","since":"2026-08-25","until":"2026-09-07"}',
            f'{{"type":"date_range","since":"2026-09-08","until":"{expected_end}"}}',
        ]
    )


@freeze_time("2026-09-15T06:00:00Z")
def test_incremental_conversions_end_date_is_clamped_and_state_stays_in_range(requests_mock: Mocker) -> None:
    _mock_page(requests_mock, "/campaigns?limit=500", "cmpn_1")
    row = {"entity_id": "cmpn_1", "date": "2026-09-13", "conversions": 3}
    requests_mock.post(
        f"{_URL}/conversions/insights",
        json={"object": "list", "data": [row], "count": 1, "account_currency": "USD"},
    )
    config = {"api_key": "test-key", "start_date": "2026-09-01", "end_date": "2026-12-31"}

    output = _read("campaign_conversions", SyncMode.incremental, config=config)

    actual_time_ranges = [
        value for request in requests_mock.request_history if request.method == "POST" for value in request.json()["time_ranges"]
    ]
    assert actual_time_ranges == ['{"type":"date_range","since":"2026-09-01","until":"2026-09-14"}']
    assert output.most_recent_state.stream_state.state["date"] <= "2026-09-14"


@freeze_time("2026-09-15T06:00:00Z")
def test_incremental_insights_default_lookback_is_32_days(requests_mock: Mocker) -> None:
    _mock_empty_insights(requests_mock)
    state = StateBuilder().with_stream_state("campaign_insights", {"readable_time": "2026-09-13"}).build()
    config = {"api_key": "test-key"}

    _read("campaign_insights", SyncMode.incremental, state, config)

    actual_time_ranges = [
        value for request in requests_mock.request_history for value in parse_qs(urlsplit(request.url).query).get("time_ranges[]", [])
    ]
    assert sorted(actual_time_ranges) == sorted(
        [
            '{"type":"date_range","since":"2026-08-12","until":"2026-08-25"}',
            '{"type":"date_range","since":"2026-08-26","until":"2026-09-08"}',
            '{"type":"date_range","since":"2026-09-09","until":"2026-09-14"}',
        ]
    )
