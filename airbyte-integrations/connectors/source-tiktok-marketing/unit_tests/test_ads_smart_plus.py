# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime
from pathlib import Path

import pytest
import requests_mock as rm
import yaml

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder

from .conftest import _YAML_FILE_PATH


def _load_manifest():
    with open(_YAML_FILE_PATH) as f:
        return yaml.safe_load(f)


def test_ads_stream_has_no_record_filter():
    """The ads stream should not filter out records — the CDK handles missing cursor fields."""
    manifest = _load_manifest()
    ads_def = manifest["definitions"]["ads_stream"]
    record_selector = ads_def["retriever"]["record_selector"]
    assert (
        "record_filter" not in record_selector
    ), "ads stream should not have a record_filter; the CDK now handles records with missing cursor fields gracefully"


def test_ads_schema_modify_time_is_nullable():
    """modify_time must be nullable to accommodate Smart+ ads that lack this field."""
    manifest = _load_manifest()
    modify_time = manifest["definitions"]["schemas"]["ads"]["properties"]["modify_time"]
    field_type = modify_time["type"]
    assert (
        isinstance(field_type, list) and "null" in field_type
    ), f"modify_time type should be nullable (e.g. ['null', 'string']), got {field_type}"


@pytest.mark.parametrize(
    "records,expected_count",
    [
        pytest.param(
            [
                {"ad_id": "1", "modify_time": "2024-06-01 00:00:00", "advertiser_id": "12345"},
                {"ad_id": "2", "modify_time": None, "advertiser_id": "12345", "smart_plus_ad_id": "sp_1"},
                {"ad_id": "3", "modify_time": "2024-06-02 00:00:00", "advertiser_id": "12345"},
            ],
            3,
            id="smart_plus_ad_without_modify_time_is_included",
        ),
        pytest.param(
            [
                {"ad_id": "4", "modify_time": None, "advertiser_id": "12345", "smart_plus_ad_id": "sp_2"},
            ],
            1,
            id="only_smart_plus_ad_without_modify_time",
        ),
    ],
)
def test_ads_stream_emits_records_with_null_modify_time(records, expected_count):
    """Records with null modify_time (Smart+ ads) must not be dropped."""
    config = {
        "access_token": "TOKEN",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "environment": {"advertiser_id": "12345"},
    }

    catalog = CatalogBuilder().with_stream("ads", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=[])

    with rm.Mocker() as m:
        m.get(
            "https://business-api.tiktok.com/open_api/v1.3/ad/get/",
            json={
                "code": 0,
                "message": "ok",
                "data": {
                    "list": records,
                    "page_info": {"page": 1, "page_size": 1000, "total_page": 1, "total_number": len(records)},
                },
            },
        )
        messages = list(source.read(logger=None, config=config, catalog=catalog, state=[]))

    record_messages = [msg for msg in messages if msg.type == Type.RECORD]
    assert (
        len(record_messages) == expected_count
    ), f"Expected {expected_count} records but got {len(record_messages)}; records with null modify_time should not be filtered out"


@pytest.mark.parametrize("cursorless_partition_has_state", [True, False], ids=["with_partition_state", "without_partition_state"])
def test_ads_incremental_filters_old_records_and_preserves_smart_plus_state(
    cursorless_partition_has_state: bool, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    config = {
        "access_token": "TOKEN",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
    }
    advertiser_a, advertiser_b = "12345", "67890"
    input_cursors = {advertiser_a: "2024-06-02 00:00:00Z"}
    if cursorless_partition_has_state:
        input_cursors[advertiser_b] = "2024-08-01 00:00:00Z"
    state = (
        StateBuilder()
        .with_stream_state(
            "ads",
            {
                "states": [
                    {"partition": {"advertiser_id": advertiser_id, "parent_slice": {}}, "cursor": {"modify_time": cursor}}
                    for advertiser_id, cursor in input_cursors.items()
                ]
            },
        )
        .build()
    )
    records_by_advertiser = {
        advertiser_a: [
            {"ad_id": 1, "advertiser_id": 12345, "modify_time": "2024-05-31 00:00:00"},
            {"ad_id": 2, "advertiser_id": 12345, "smart_plus_ad_id": 102},
            {"ad_id": 3, "advertiser_id": 12345, "modify_time": "2024-06-05 00:00:00"},
            {"ad_id": 4, "advertiser_id": 12345, "modify_time": "2024-06-01 23:59:59"},
            {"ad_id": 5, "advertiser_id": 12345, "modify_time": "2024-06-03 00:00:00"},
            {"ad_id": 6, "advertiser_id": 12345, "smart_plus_ad_id": 106, "modify_time": None},
        ],
        advertiser_b: [
            {"ad_id": 7, "advertiser_id": 67890, "smart_plus_ad_id": 107},
            {"ad_id": 8, "advertiser_id": 67890, "smart_plus_ad_id": 108, "modify_time": None},
        ],
    }
    catalog = CatalogBuilder().with_stream("ads", SyncMode.incremental).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)

    with rm.Mocker() as m:
        m.get(
            "https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/",
            json={"code": 0, "message": "ok", "data": {"list": [{"advertiser_id": advertiser_a}, {"advertiser_id": advertiser_b}]}},
        )
        for advertiser_id, records in records_by_advertiser.items():
            m.get(
                f"https://business-api.tiktok.com/open_api/v1.3/ad/get/?advertiser_id={advertiser_id}",
                json={
                    "code": 0,
                    "message": "ok",
                    "data": {
                        "list": records,
                        "page_info": {"page": 1, "page_size": 1000, "total_page": 1, "total_number": len(records)},
                    },
                },
            )
        messages = list(source.read(logger=None, config=config, catalog=catalog, state=state))

    assert not [msg.trace.error for msg in messages if msg.type == Type.TRACE and msg.trace.error]
    emitted_records = [msg.record.data for msg in messages if msg.type == Type.RECORD]
    assert sorted(record["ad_id"] for record in emitted_records) == [2, 3, 5, 6, 7, 8]
    for record in emitted_records:
        if record.get("modify_time") is not None:
            assert datetime.strptime(record["modify_time"], "%Y-%m-%d %H:%M:%S") >= datetime.strptime(
                input_cursors[str(record["advertiser_id"])], "%Y-%m-%d %H:%M:%SZ"
            )

    ads_states = [
        msg.state.stream.stream_state for msg in messages if msg.type == Type.STATE and msg.state.stream.stream_descriptor.name == "ads"
    ]
    assert ads_states, "The incremental read must emit ads state"
    assert ads_states[-1].use_global_cursor is False
    for ads_state in ads_states:
        partition_cursors = {entry["partition"]["advertiser_id"]: entry["cursor"] for entry in ads_state.states}
        if cursorless_partition_has_state:
            assert partition_cursors[advertiser_b] == {"modify_time": input_cursors[advertiser_b]}
        elif advertiser_b in partition_cursors:
            assert partition_cursors[advertiser_b] == {"modify_time": "2024-01-01 00:00:00Z"}
    assert partition_cursors[advertiser_a] == {"modify_time": "2024-06-05 00:00:00Z"}
