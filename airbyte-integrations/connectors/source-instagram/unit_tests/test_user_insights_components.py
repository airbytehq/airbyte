# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock, patch

import pytest

from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig, SubstreamPartitionRouter
from airbyte_cdk.sources.types import StreamSlice


@pytest.mark.parametrize(
    "metrics_response,expected_record",
    [
        pytest.param(
            [
                {
                    "name": "follower_count",
                    "period": "day",
                    "values": [{"value": 1, "end_time": "2025-06-06T07:00:00+0000"}],
                },
                {
                    "name": "reach",
                    "period": "day",
                    "values": [{"value": 20, "end_time": "2025-06-06T07:00:00+0000"}],
                },
            ],
            {
                "follower_count": 1,
                "reach": 20,
                "date": "2025-06-06T07:00:00+0000",
            },
            id="test_day_metrics",
        ),
        pytest.param(
            [
                {
                    "name": "reach",
                    "period": "week",
                    "values": [{"value": 100, "end_time": "2025-06-07T07:00:00+0000"}],
                },
            ],
            {
                "reach_week": 100,
                "date": "2025-06-07T07:00:00+0000",
            },
            id="test_week_metrics",
        ),
        pytest.param(
            [
                {
                    "name": "reach",
                    "period": "days_28",
                    "values": [{"value": 1000, "end_time": "2025-06-08T07:00:00+0000"}],
                },
            ],
            {
                "reach_days_28": 1000,
                "date": "2025-06-08T07:00:00+0000",
            },
            id="test_days_28_metrics",
        ),
        pytest.param(
            [
                {
                    "name": "online_followers",
                    "period": "lifetime",
                    "values": [{"value": {"0": 159, "1": 157}, "end_time": "2025-06-09T07:00:00+0000"}],
                },
            ],
            {
                "online_followers": {"0": 159, "1": 157},
                "date": "2025-06-09T07:00:00+0000",
            },
            id="test_lifetime_metrics",
        ),
    ],
)
def test_user_insights_extractor(components_module, metrics_response, expected_record):
    response = {
        "data": metrics_response,
        "paging": {
            "previous": "https://graph.facebook.com/v21.0/17841408147298757/insights?since=1749074099&until=1749160499&metric=follower_count%2Creach&period=day",
            "next": "https://graph.facebook.com/v21.0/17841408147298757/insights?since=1749246901&until=1749333301&metric=follower_count%2Creach&period=day",
        },
    }

    decoder = MagicMock()
    decoder.decode.return_value = [response]

    extractor = components_module.UserInsightsExtractor(field_path=["data"], decoder=decoder, config={}, parameters={})
    records = list(extractor.extract_records(response))
    assert len(records) == 1
    day_record = records[0]
    assert day_record == expected_record


def test_user_insights_substream_partition_router(components_module):
    parent_stream_configs = [
        ParentStreamConfig(
            stream=MagicMock(),
            parent_key="account",
            partition_field="business_account_id",
            config={},
            parameters={},
        )
    ]

    with patch.object(
        SubstreamPartitionRouter,
        "stream_slices",
        return_value=[
            StreamSlice(
                partition={"business_account_id": {"business_account_id": "12345", "page_id": "1"}}, cursor_slice={}, extra_fields={}
            ),
            StreamSlice(
                partition={"business_account_id": {"business_account_id": "67890", "page_id": "2"}}, cursor_slice={}, extra_fields={}
            ),
        ],
    ):
        partition_router = components_module.UserInsightsSubstreamPartitionRouter(
            parent_stream_configs=parent_stream_configs, config={}, parameters={}
        )

        slices = list(partition_router.stream_slices())

        assert len(slices) == 2
        assert slices[0] == StreamSlice(partition={"business_account_id": "12345"}, cursor_slice={}, extra_fields={"page_id": "1"})
        assert slices[1] == StreamSlice(partition={"business_account_id": "67890"}, cursor_slice={}, extra_fields={"page_id": "2"})


@pytest.mark.parametrize(
    "original_value,field_schema,expected_value",
    [
        pytest.param(
            "2025-06-06T07:00:00+0000",
            {"format": "date-time", "airbyte_type": "timestamp_with_timezone"},
            "2025-06-06T07:00:00+00:00",
            id="test_transform_timestamp_with_timezone",
        ),
        pytest.param(
            "string_value",
            {"format": "string"},
            "string_value",
            id="test_transform_string_value",
        ),
        pytest.param(
            10000000000,
            {"format": "date-time", "airbyte_type": "integer"},
            10000000000,
            id="test_transform_datetime_that_is_not_timestamp_with_timezone_type",
        ),
    ],
)
def test_rfc3339_datetime_schema_normalization(components_module, original_value, field_schema, expected_value):
    type_transformer = components_module.RFC3339DatetimeSchemaNormalization()
    transform = type_transformer.get_transform_function()

    transformed_value = transform(original_value=original_value, field_schema=field_schema)
    assert transformed_value == expected_value
