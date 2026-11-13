#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

import pytest
from components import AdAccountRecordExtractor, CustomReportStatusChunkStateMigration, StatusChunkPartitionRouter

from airbyte_cdk.models import FailureType
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .conftest import get_stream_by_name, read_from_stream


os.environ["REQUEST_CACHE_PATH"] = "/tmp"
_ANY_STREAM_NAME = "any_stream_name"
_RETRY_AFTER_HEADER = "XRetry-After"
_A_MAX_TIME = 10


def test_parse_response_with_sensitive_data(requests_mock, test_config):
    """Test that sensitive data is removed"""
    requests_mock.get(
        url="https://api.pinterest.com/v5/catalogs/feeds",
        json={"items": [{"id": "CatalogsFeeds1", "credentials": {"password": "bla"}}]},
    )
    actual_response = [
        record.record.data for record in read_from_stream(test_config, "catalogs_feeds", sync_mode=SyncMode.full_refresh).records
    ]
    assert actual_response == [{"id": "CatalogsFeeds1"}]


@pytest.mark.parametrize(
    ("stream_name", "stream_slice", "expected_path"),
    (
        ("boards", None, "boards"),
        ("ad_accounts", None, "ad_accounts"),
        ("board_sections", {"id": "123"}, "boards/123/sections"),
        ("board_pins", {"id": "123"}, "boards/123/pins"),
        ("board_section_pins", {"parent_slice": {"id": "234"}, "id": "123"}, "boards/234/sections/123/pins"),
        ("ad_account_analytics", {"id": "123"}, "ad_accounts/123/analytics"),
        ("campaigns", {"id": "123"}, "ad_accounts/123/campaigns"),
        (
            "campaign_analytics",
            {"parent_slice": {"id": "234"}, "id": "123"},
            "ad_accounts/234/campaigns/analytics?campaign_ids=123",
        ),
        ("ad_groups", {"id": "123"}, "ad_accounts/123/ad_groups"),
        (
            "ad_group_analytics",
            {"parent_slice": {"id": "234"}, "id": "123"},
            "ad_accounts/234/ad_groups/analytics?ad_group_ids=123",
        ),
        ("ads", {"id": "123"}, "ad_accounts/123/ads"),
        ("ad_analytics", {"parent_slice": {"id": "234"}, "id": "123"}, "ad_accounts/234/ads/analytics?ad_ids=123"),
        ("catalogs", None, "catalogs"),
        ("catalogs_feeds", None, "catalogs/feeds"),
        ("catalogs_product_groups", None, "catalogs/product_groups"),
        (
            "keywords",
            {"parent_slice": {"id": "AD_ACCOUNT_1"}, "id": "234"},
            "ad_accounts/AD_ACCOUNT_1/keywords?ad_group_id=234",
        ),
        ("audiences", {"id": "AD_ACCOUNT_1"}, "ad_accounts/AD_ACCOUNT_1/audiences"),
        ("conversion_tags", {"id": "AD_ACCOUNT_1"}, "ad_accounts/AD_ACCOUNT_1/conversion_tags"),
        ("customer_lists", {"id": "AD_ACCOUNT_1"}, "ad_accounts/AD_ACCOUNT_1/customer_lists"),
    ),
)
def test_path(test_config, stream_name, stream_slice, expected_path):
    stream = get_stream_by_name(stream_name, test_config)
    if stream_slice:
        stream_slice = StreamSlice(partition=stream_slice, cursor_slice={})

    result = stream._stream_partition_generator._partition_factory._retriever.requester.get_path(
        stream_slice=stream_slice, stream_state=None, next_page_token=None
    )

    assert result == expected_path


def test_extract_records_with_items(test_response):
    extractor = AdAccountRecordExtractor()
    result = extractor.extract_records(test_response)
    assert result == test_response.json()["items"]


def test_extract_records_single_account(test_response_single_account):
    extractor = AdAccountRecordExtractor()
    result = extractor.extract_records(test_response_single_account)
    assert result == [{"id": "1234"}]


@pytest.mark.parametrize(
    ("kwargs", "expected_partitions"),
    [
        pytest.param({}, [{}], id="empty"),
        pytest.param(
            {"campaign_statuses": [], "ad_group_statuses": [], "ad_statuses": []},
            [{}],
            id="explicit-empty-lists",
        ),
        pytest.param(
            {"campaign_statuses": ["RUNNING", "PAUSED"]},
            [{"campaign_statuses_chunk": ["PAUSED", "RUNNING"]}],
            id="under-limit-sorted",
        ),
        pytest.param(
            {"campaign_statuses": ["C6", "C5", "C4", "C3", "C2", "C1"]},
            [{"campaign_statuses_chunk": ["C1", "C2", "C3", "C4", "C5", "C6"]}],
            id="exact-limit-single-chunk",
        ),
    ],
)
def test_status_chunk_partition_router_empty_and_under_limit(kwargs, expected_partitions):
    router = StatusChunkPartitionRouter(config={}, parameters={}, **kwargs)
    stream_slices = list(router.stream_slices())

    assert [stream_slice.partition for stream_slice in stream_slices] == expected_partitions
    assert all(stream_slice.cursor_slice == {} for stream_slice in stream_slices)


def test_status_chunk_partition_router_chunks_status_combinations():
    campaign_statuses = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
    ad_group_statuses = ["G1", "G2"]
    ad_statuses = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]
    router = StatusChunkPartitionRouter(
        config={},
        parameters={},
        campaign_statuses=campaign_statuses,
        ad_group_statuses=ad_group_statuses,
        ad_statuses=ad_statuses,
        level="PIN_PROMOTION",
    )

    stream_slices = list(router.stream_slices())
    partitions = [stream_slice.partition for stream_slice in stream_slices]

    assert len(partitions) == 4
    assert all(stream_slice.cursor_slice == {} for stream_slice in stream_slices)
    # Assert the full cartesian pairing, not just per-dimension chunk sets - an
    # implementation repeating some combinations while dropping others must fail here.
    campaign_chunks = (tuple(campaign_statuses[:6]), tuple(campaign_statuses[6:]))
    ad_chunks = (tuple(ad_statuses[:6]), tuple(ad_statuses[6:]))
    assert {
        (
            tuple(partition["campaign_statuses_chunk"]),
            tuple(partition["ad_group_statuses_chunk"]),
            tuple(partition["ad_statuses_chunk"]),
        )
        for partition in partitions
    } == {(campaign_chunk, tuple(ad_group_statuses), ad_chunk) for campaign_chunk in campaign_chunks for ad_chunk in ad_chunks}
    assert all(len(partition["campaign_statuses_chunk"]) <= 6 for partition in partitions)
    assert all(len(partition["ad_group_statuses_chunk"]) <= 6 for partition in partitions)
    assert all(len(partition["ad_statuses_chunk"]) <= 6 for partition in partitions)

    # Reordering the same status sets must produce identical partitions - partition keys
    # feed per-partition cursors, and a config reorder must not orphan them.
    reordered = StatusChunkPartitionRouter(
        config={},
        parameters={},
        campaign_statuses=list(reversed(campaign_statuses)),
        ad_group_statuses=list(reversed(ad_group_statuses)),
        ad_statuses=list(reversed(ad_statuses)),
        level="PIN_PROMOTION",
    )
    assert [stream_slice.partition for stream_slice in reordered.stream_slices()] == partitions


def test_status_chunk_partition_router_rejects_chunking_above_report_level():
    seven_ad_statuses = ["APPROVED", "PAUSED", "PENDING", "REJECTED", "ADVERTISER_DISABLED", "ARCHIVED", "DRAFT"]

    unsafe_router = StatusChunkPartitionRouter(config={}, parameters={}, ad_statuses=seven_ad_statuses, level="CAMPAIGN")
    with pytest.raises(AirbyteTracedException) as exc_info:
        list(unsafe_router.stream_slices())
    assert exc_info.value.failure_type == FailureType.config_error
    assert "ad_statuses" in exc_info.value.message

    safe_router = StatusChunkPartitionRouter(config={}, parameters={}, ad_statuses=seven_ad_statuses, level="PIN_PROMOTION")
    assert len(list(safe_router.stream_slices())) == 2

    under_limit_router = StatusChunkPartitionRouter(config={}, parameters={}, ad_statuses=["APPROVED"], level="ADVERTISER")
    assert len(list(under_limit_router.stream_slices())) == 1


def test_status_chunk_state_migration_copies_legacy_account_cursors():
    campaign_statuses = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
    migration = CustomReportStatusChunkStateMigration(
        config={},
        campaign_statuses=campaign_statuses,
        ad_group_statuses=["G1"],
        ad_statuses=["A1"],
    )
    already_chunked_entry = {
        "partition": {"id": 789, "parent_slice": {}, "campaign_statuses_chunk": ["C1"]},
        "cursor": {"DATE": "2026-05-22"},
    }
    legacy_state = {
        "states": [
            {"partition": {"id": 123, "parent_slice": {}}, "cursor": {"DATE": "2026-05-20"}},
            {"partition": {"id": 456, "parent_slice": {}}, "cursor": {"DATE": "2026-05-18"}},
            already_chunked_entry,
        ],
        "state": {"DATE": "2026-05-18"},
        "use_global_cursor": False,
        "lookback_window": 42,
    }

    assert migration.should_migrate(legacy_state) is True
    migrated = migration.migrate(legacy_state)

    # 2 legacy accounts x 2 campaign chunks (x 1 ad-group chunk x 1 ad chunk) + 1 passthrough
    assert len(migrated["states"]) == 5
    assert already_chunked_entry in migrated["states"]
    fanned_out = [entry for entry in migrated["states"] if entry is not already_chunked_entry]
    assert {
        (entry["partition"]["id"], tuple(entry["partition"]["campaign_statuses_chunk"]), entry["cursor"]["DATE"]) for entry in fanned_out
    } == {
        (account_id, campaign_chunk, cursor_date)
        for account_id, cursor_date in ((123, "2026-05-20"), (456, "2026-05-18"))
        for campaign_chunk in (tuple(campaign_statuses[:6]), tuple(campaign_statuses[6:]))
    }
    assert all(entry["partition"]["parent_slice"] == {} for entry in fanned_out)
    assert all(entry["partition"]["ad_group_statuses_chunk"] == ["G1"] for entry in fanned_out)
    assert all(entry["partition"]["ad_statuses_chunk"] == ["A1"] for entry in fanned_out)
    # Top-level per-partition-cursor keys must survive the migration untouched.
    assert migrated["state"] == {"DATE": "2026-05-18"}
    assert migrated["use_global_cursor"] is False
    assert migrated["lookback_window"] == 42


def test_status_chunk_state_migration_skips_when_filters_absent_or_already_chunked():
    migration = CustomReportStatusChunkStateMigration(config={}, campaign_statuses=["RUNNING"])
    already_chunked = {
        "states": [
            {
                "partition": {"id": "123", "campaign_statuses_chunk": ["RUNNING"]},
                "cursor": {"DATE": "2026-05-20"},
            }
        ]
    }
    global_cursor_only = {"states": [], "state": {"DATE": "2026-05-20"}, "use_global_cursor": True}

    assert CustomReportStatusChunkStateMigration(config={}).should_migrate({"states": [{"partition": {"id": "123"}}]}) is False
    assert migration.should_migrate(already_chunked) is False
    assert migration.should_migrate({"DATE": "2026-05-20"}) is False
    assert migration.should_migrate({}) is False
    assert migration.should_migrate(global_cursor_only) is False
    # An entry without a cursor is not a legacy per-partition entry - never fan it out.
    assert migration.should_migrate({"states": [{"partition": {"id": "123", "parent_slice": {}}}]}) is False
