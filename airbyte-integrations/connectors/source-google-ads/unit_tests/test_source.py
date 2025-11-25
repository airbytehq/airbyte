#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from collections import namedtuple
from unittest.mock import MagicMock, Mock, call

import pendulum
import pytest
from source_google_ads.components import GoogleAdsPerPartitionStateMigration, KeysToSnakeCaseGoogleAdsTransformation
from source_google_ads.models import CustomerModel
from source_google_ads.source import SourceGoogleAds
from source_google_ads.streams import chunk_date_range

from airbyte_cdk import Record
from airbyte_cdk.models import (
    AirbyteStream,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    TraceType,
)
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.test.entrypoint_wrapper import read

from .conftest import get_source


@pytest.fixture
def mock_get_customers(mocker):
    mocker.patch(
        "source_google_ads.source.SourceGoogleAds.get_customers",
        Mock(return_value=[CustomerModel(is_manager_account=False, time_zone="Europe/Berlin", id="8765")]),
    )


@pytest.fixture()
def mock_fields_meta_data():
    DataType = namedtuple("DataType", ["name"])
    Node = namedtuple("Node", ["data_type", "name", "enum_values", "is_repeated"])
    nodes = (
        Node(DataType("RESOURCE_NAME"), "campaign.accessible_bidding_strategy", [], False),
        Node(
            DataType("ENUM"),
            "segments.ad_destination_type",
            [
                "APP_DEEP_LINK",
                "APP_STORE",
                "LEAD_FORM",
                "LOCATION_LISTING",
                "MAP_DIRECTIONS",
                "MESSAGE",
                "NOT_APPLICABLE",
                "PHONE_CALL",
                "UNKNOWN",
                "UNMODELED_FOR_CONVERSIONS",
                "UNSPECIFIED",
                "WEBSITE",
                "YOUTUBE",
            ],
            False,
        ),
        Node(DataType("DATE"), "campaign.start_date", [], is_repeated=False),
        Node(DataType("DATE"), "campaign.end_date", [], False),
        Node(DataType("DATE"), "segments.date", [], False),
        Node(
            DataType("ENUM"),
            "accessible_bidding_strategy.target_impression_share.location",
            ["ABSOLUTE_TOP_OF_PAGE", "ANYWHERE_ON_PAGE", "TOP_OF_PAGE", "UNKNOWN", "UNSPECIFIED"],
            False,
        ),
        Node(DataType("STRING"), "campaign.name", [], False),
        Node(DataType("DOUBLE"), "campaign.optimization_score", [], False),
        Node(DataType("RESOURCE_NAME"), "campaign.resource_name", [], False),
        Node(DataType("INT32"), "campaign.shopping_setting.campaign_priority", [], False),
        Node(DataType("INT64"), "campaign.shopping_setting.merchant_id", [], False),
        Node(DataType("BOOLEAN"), "campaign_budget.explicitly_shared", [], False),
        Node(DataType("MESSAGE"), "bidding_strategy.enhanced_cpc", [], False),
    )
    return Mock(get_fields_metadata=Mock(return_value={node.name: node for node in nodes}))


def test_chunk_date_range():
    start_date = "2021-03-04"
    end_date = "2021-05-04"
    conversion_window = 14
    slices = list(
        chunk_date_range(
            start_date=start_date,
            end_date=end_date,
            conversion_window=conversion_window,
            slice_duration=pendulum.Duration(days=9),
            time_zone="UTC",
        )
    )
    assert [
        {"start_date": "2021-02-18", "end_date": "2021-02-27"},
        {"start_date": "2021-02-28", "end_date": "2021-03-09"},
        {"start_date": "2021-03-10", "end_date": "2021-03-19"},
        {"start_date": "2021-03-20", "end_date": "2021-03-29"},
        {"start_date": "2021-03-30", "end_date": "2021-04-08"},
        {"start_date": "2021-04-09", "end_date": "2021-04-18"},
        {"start_date": "2021-04-19", "end_date": "2021-04-28"},
        {"start_date": "2021-04-29", "end_date": "2021-05-04"},
    ] == slices


def test_streams_count(config):
    streams = get_source(config).streams(config)
    expected_streams_number = 30
    assert len(streams) == expected_streams_number


def test_read_missing_stream(config):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="fake_stream",
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            ),
            # FIXME In the CDK today, there is a bug where the last stream does not exist, the trace message is not sent.
            # Until this is fixed, we will have this stream added here
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="ad_group",
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            ),
        ]
    )

    source = SourceGoogleAds(catalog, config, None)
    output = read(source, config, catalog)
    fake_stream_statuses = list(
        filter(
            lambda message: message.trace.type == TraceType.STREAM_STATUS
            and message.trace.stream_status.stream_descriptor.name == "fake_stream",
            output.trace_messages,
        )
    )
    assert len(fake_stream_statuses) == 1
    assert fake_stream_statuses[0].trace.stream_status.status == AirbyteStreamStatus.INCOMPLETE


@pytest.mark.parametrize(
    "input_state, record_and_slices, expected",
    [
        # no partitions ⇒ empty
        ({}, [], {}),
        # single partition ⇒ one migrated state
        (
            {"123": {"segments.date": "2120-10-10"}},
            [
                # (record, slice)
                ({"id": "123", "clientCustomer": "123"}, {"customer_id": "456"})
            ],
            {
                "states": [
                    {
                        "partition": {"customer_id": "123", "parent_slice": {"customer_id": "456", "parent_slice": {}}},
                        "cursor": {"segments.date": "2120-10-10"},
                    }
                ],
                "state": {"segments.date": "2120-10-10"},
            },
        ),
        # multiple partitions ⇒ only those matching state, with earliest date
        (
            {"a": {"segments.date": "2020-01-02"}, "b": {"segments.date": "2020-01-01"}, "z": {"segments.date": "2021-01-01"}},
            [
                ({"id": "b", "clientCustomer": "b"}, {"customer_id": "p1"}),
                ({"id": "a", "clientCustomer": "a"}, {"customer_id": "p2"}),
                # a record that won't match legacy state
                ({"id": "x", "clientCustomer": "x"}, {"customer_id": "p3"}),
            ],
            {
                "states": [
                    {
                        "partition": {"customer_id": "b", "parent_slice": {"customer_id": "p1", "parent_slice": {}}},
                        "cursor": {"segments.date": "2020-01-01"},
                    },
                    {
                        "partition": {"customer_id": "a", "parent_slice": {"customer_id": "p2", "parent_slice": {}}},
                        "cursor": {"segments.date": "2020-01-02"},
                    },
                ],
                "state": {"segments.date": "2020-01-01"},
            },
        ),
        # none have the cursor field ⇒ empty
        ({"x": {"foo": "bar"}, "y": {"baz": 42}}, [], {}),
        # already migrated state ⇒ unchanged
        (
            {"use_global_cursor": True, "lookback_window": 15, "state": {"segments.date": "2020-01-02"}},
            [],
            {"use_global_cursor": True, "lookback_window": 15, "state": {"segments.date": "2020-01-02"}},
        ),
    ],
)
def test_state_migration(input_state, record_and_slices, expected):
    # Create a fake customer_client_stream
    stream_mock = MagicMock()

    # Define what _read_parent_stream will yield
    stream_mock.generate_partitions.return_value = (mock_partition(_slice, record) for record, _slice in record_and_slices)

    def fake_read_records(stream_slice, sync_mode):
        return (r for r, s in record_and_slices if s == stream_slice)

    stream_mock.read_records.side_effect = fake_read_records

    migrator = GoogleAdsPerPartitionStateMigration(config=None, customer_client_stream=stream_mock)

    assert migrator.migrate(input_state) == expected


def mock_partition(_slice, record):
    partition = Mock(spec=Partition)
    partition.read.return_value = [Record(record, "stream_name", _slice)]
    return partition


_ANY_VALUE = -1


@pytest.mark.parametrize(
    "input_keys, expected_keys",
    [
        (
            {"FirstName": _ANY_VALUE, "lastName": _ANY_VALUE},
            {"first_name": _ANY_VALUE, "last_name": _ANY_VALUE},
        ),
        (
            {"123Number": _ANY_VALUE, "456Another123": _ANY_VALUE},
            {"123number": _ANY_VALUE, "456another123": _ANY_VALUE},
        ),
        (
            {
                "NestedRecord": {"FirstName": _ANY_VALUE, "lastName": _ANY_VALUE},
                "456Another123": _ANY_VALUE,
            },
            {
                "nested_record": {"first_name": _ANY_VALUE, "last_name": _ANY_VALUE},
                "456another123": _ANY_VALUE,
            },
        ),
        (
            {"hello@world": _ANY_VALUE, "test#case": _ANY_VALUE},
            {"hello_world": _ANY_VALUE, "test_case": _ANY_VALUE},
        ),
        (
            {"MixedUPCase123": _ANY_VALUE, "lowercaseAnd123": _ANY_VALUE},
            {"mixed_upcase123": _ANY_VALUE, "lowercase_and123": _ANY_VALUE},
        ),
        ({"Café": _ANY_VALUE, "Naïve": _ANY_VALUE}, {"cafe": _ANY_VALUE, "naive": _ANY_VALUE}),
        (
            {
                "This is a full sentence": _ANY_VALUE,
                "Another full sentence with more words": _ANY_VALUE,
            },
            {
                "this_is_a_full_sentence": _ANY_VALUE,
                "another_full_sentence_with_more_words": _ANY_VALUE,
            },
        ),
    ],
)
def test_keys_transformation(input_keys, expected_keys):
    KeysToSnakeCaseGoogleAdsTransformation().transform(input_keys)
    assert input_keys == expected_keys
