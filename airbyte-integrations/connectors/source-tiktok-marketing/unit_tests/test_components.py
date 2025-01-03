# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest
from source_tiktok_marketing import SourceTiktokMarketing
from source_tiktok_marketing.components.advertiser_ids_partition_router import (
    MultipleAdvertiserIdsPerPartition,
    SingleAdvertiserIdPerPartition,
)
from source_tiktok_marketing.components.hourly_datetime_based_cursor import HourlyDatetimeBasedCursor
from source_tiktok_marketing.components.semi_incremental_record_filter import PerPartitionRecordFilter
from source_tiktok_marketing.components.transformations import TransformEmptyMetrics

from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.types import StreamSlice


@pytest.mark.parametrize(
    "config, expected",
    [
        ({"credentials": {"advertiser_id": "11111111111"}}, "11111111111"),
        ({"environment": {"advertiser_id": "2222222222"}}, "2222222222"),
        ({"credentials": {"access_token": "access_token"}}, None),
    ],
)
def test_get_partition_value_from_config(config, expected):
    router = MultipleAdvertiserIdsPerPartition(
        parent_stream_configs=[MagicMock()],
        config=config,
        parameters={
            "path_in_config": [["credentials", "advertiser_id"], ["environment", "advertiser_id"]],
            "partition_field": "advertiser_id",
        },
    )
    actual = router.get_partition_value_from_config()
    assert actual == expected


@pytest.mark.parametrize(
    "config, expected, json_data",
    [
        (
            {"credentials": {"auth_type": "oauth2.0", "advertiser_id": "11111111111"}},
            [{"advertiser_ids": '["11111111111"]', "parent_slice": {}}],
            None,
        ),
        ({"environment": {"advertiser_id": "2222222222"}}, [{"advertiser_ids": '["2222222222"]', "parent_slice": {}}], None),
        (
            {"credentials": {"auth_type": "oauth2.0", "access_token": "access_token"}},
            [{"advertiser_ids": '["11111111", "22222222"]', "parent_slice": {}}],
            {
                "code": 0,
                "message": "ok",
                "data": {
                    "list": [
                        {"advertiser_id": "11111111", "advertiser_name": "name"},
                        {"advertiser_id": "22222222", "advertiser_name": "name"},
                    ]
                },
            },
        ),
    ],
)
def test_stream_slices_multiple(config, expected, requests_mock, json_data):
    advertiser_ids_stream = [s for s in SourceTiktokMarketing().streams(config=config) if s.name == "advertiser_ids"]
    advertiser_ids_stream = advertiser_ids_stream[0] if advertiser_ids_stream else MagicMock()

    router = MultipleAdvertiserIdsPerPartition(
        parent_stream_configs=[
            ParentStreamConfig(
                partition_field="advertiser_ids", config=config, parent_key="advertiser_id", stream=advertiser_ids_stream, parameters={}
            )
        ],
        config=config,
        parameters={
            "path_in_config": [["credentials", "advertiser_id"], ["environment", "advertiser_id"]],
            "partition_field": "advertiser_ids",
        },
    )
    if json_data:
        requests_mock.get("https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/", json=json_data)
    actual = list(router.stream_slices())
    assert actual == expected


@pytest.mark.parametrize(
    "config, expected, json_data",
    [
        (
            {"credentials": {"auth_type": "oauth2.0", "advertiser_id": "11111111111"}},
            [{"advertiser_id": "11111111111", "parent_slice": {}}],
            None,
        ),
        ({"environment": {"advertiser_id": "2222222222"}}, [{"advertiser_id": "2222222222", "parent_slice": {}}], None),
        (
            {"credentials": {"auth_type": "oauth2.0", "access_token": "access_token"}},
            [{"advertiser_id": "11111111", "parent_slice": {}}, {"advertiser_id": "22222222", "parent_slice": {}}],
            {
                "code": 0,
                "message": "ok",
                "data": {
                    "list": [
                        {"advertiser_id": "11111111", "advertiser_name": "name"},
                        {"advertiser_id": "22222222", "advertiser_name": "name"},
                    ]
                },
            },
        ),
    ],
)
def test_stream_slices_single(config, expected, requests_mock, json_data):
    advertiser_ids_stream = [s for s in SourceTiktokMarketing().streams(config=config) if s.name == "advertiser_ids"]
    advertiser_ids_stream = advertiser_ids_stream[0] if advertiser_ids_stream else MagicMock()

    router = SingleAdvertiserIdPerPartition(
        parent_stream_configs=[
            ParentStreamConfig(
                partition_field="advertiser_id", config=config, parent_key="advertiser_id", stream=advertiser_ids_stream, parameters={}
            )
        ],
        config=config,
        parameters={
            "path_in_config": [["credentials", "advertiser_id"], ["environment", "advertiser_id"]],
            "partition_field": "advertiser_id",
        },
    )
    if json_data:
        requests_mock.get("https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/", json=json_data)
    actual = list(router.stream_slices())
    assert actual == expected


@pytest.mark.parametrize(
    "records, state, slice, expected",
    [
        (
            [{"id": 1, "start_time": "2024-01-01"}, {"id": 2, "start_time": "2024-01-01"}],
            {},
            {},
            [{"id": 1, "start_time": "2024-01-01"}, {"id": 2, "start_time": "2024-01-01"}],
        ),
        (
            [{"advertiser_id": 1, "start_time": "2022-01-01"}, {"advertiser_id": 1, "start_time": "2024-01-02"}],
            {"states": [{"partition": {"advertiser_id": 1, "parent_slice": {}}, "cursor": {"start_time": "2023-12-31"}}]},
            {"advertiser_id": 1},
            [{"advertiser_id": 1, "start_time": "2024-01-02"}],
        ),
        (
            [{"advertiser_id": 2, "start_time": "2022-01-01"}, {"advertiser_id": 2, "start_time": "2024-01-02"}],
            {"states": [{"partition": {"advertiser_id": 1, "parent_slice": {}}, "cursor": {"start_time": "2023-12-31"}}]},
            {"advertiser_id": 2},
            [{"advertiser_id": 2, "start_time": "2022-01-01"}, {"advertiser_id": 2, "start_time": "2024-01-02"}],
        ),
    ],
)
def test_record_filter(records, state, slice, expected):
    config = {"credentials": {"auth_type": "oauth2.0", "advertiser_id": "11111111111"}}
    record_filter = PerPartitionRecordFilter(
        config=config,
        parameters={"partition_field": "advertiser_id"},
        condition="{{ record['start_time'] >= stream_state.get('start_time', config.get('start_date', '')) }}",
    )
    filtered_records = list(
        record_filter.filter_records(records=records, stream_state=state, stream_slice=StreamSlice(partition=slice, cursor_slice={}))
    )
    assert filtered_records == expected


def test_hourly_datetime_based_cursor():
    config = {
        "credentials": {"auth_type": "oauth2.0", "advertiser_id": "11111111111"},
        "start_date": "2022-01-01",
        "end_date": "2022-01-02",
    }

    cursor = HourlyDatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="{{ config.get('start_date', '2016-09-01') }}", datetime_format="%Y-%m-%d", parameters={}),
        end_datetime=MinMaxDatetime(datetime="{{ config.get('end_date', today_utc()) }}", datetime_format="%Y-%m-%d", parameters={}),
        step="P1D",
        cursor_granularity="PT1H",
        config=config,
        cursor_field="stat_time_hour",
        datetime_format="%Y-%m-%d",
        cursor_datetime_formats=["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"],
        parameters={},
    )
    cursor._cursor = "2022-01-01 00:00:00"
    partition_daterange = list(cursor.stream_slices())
    assert partition_daterange == [
        {"start_time": "2022-01-01", "end_time": "2022-01-01"},
        {"start_time": "2022-01-02", "end_time": "2022-01-02"},
    ]

    cursor._cursor = "2022-01-01 10:00:00"
    partition_daterange = list(cursor.stream_slices())
    assert partition_daterange == [
        {"start_time": "2022-01-01", "end_time": "2022-01-01"},
        {"start_time": "2022-01-02", "end_time": "2022-01-02"},
    ]


@pytest.mark.parametrize(
    "record, expected",
    [
        ({"metrics": {"metric_1": "not empty", "metric_2": "-"}}, {"metrics": {"metric_1": "not empty", "metric_2": None}}),
        ({"metrics": {"metric_1": "not empty", "metric_2": "not empty"}}, {"metrics": {"metric_1": "not empty", "metric_2": "not empty"}}),
        (
            {"dimensions": {"dimension_1": "not empty", "dimension_2": "not empty"}},
            {"dimensions": {"dimension_1": "not empty", "dimension_2": "not empty"}},
        ),
        ({}, {}),
    ],
)
def test_transform_empty_metrics(record, expected):
    transformer = TransformEmptyMetrics()
    actual_record = transformer.transform(record)
    assert actual_record == expected
