#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import re
from collections import namedtuple
from unittest.mock import MagicMock, Mock, call

import pendulum
import pytest
from source_google_ads.components import GoogleAdsPerPartitionStateMigration, KeysToSnakeCaseGoogleAdsTransformation
from source_google_ads.models import CustomerModel
from source_google_ads.source import SourceGoogleAds
from source_google_ads.streams import chunk_date_range

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, FailureType, SyncMode

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


def test_streams_count(config, mock_get_customers):
    streams = get_source(config).streams(config)
    expected_streams_number = 30
    assert len(streams) == expected_streams_number


def test_read_missing_stream(config, mock_get_customers):
    source = SourceGoogleAds(config, None, None)

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
            )
        ]
    )

    with pytest.raises(AirbyteTracedException) as e:
        list(source.read(logging.getLogger("airbyte"), config=config, catalog=catalog))
    assert e.value.failure_type == FailureType.config_error


def mock_send_request(query: str, customer_id: str, login_customer_id: str = "default"):
    print(query, customer_id, login_customer_id)
    if customer_id == "123":
        if "WHERE customer_client.status in ('active')" in query:
            return [
                [
                    {"customer_client.id": "123", "customer_client.status": "active"},
                ]
            ]
        else:
            return [
                [
                    {"customer_client.id": "123", "customer_client.status": "active"},
                    {"customer_client.id": "456", "customer_client.status": "disabled"},
                ]
            ]
    else:
        return [
            [
                {"customer_client.id": "789", "customer_client.status": "active"},
            ]
        ]


@pytest.mark.parametrize(
    "customer_status_filter, expected_ids, send_request_calls",
    [
        (
            [],
            ["123", "456", "789"],
            [
                call(
                    "SELECT customer_client.client_customer, customer_client.level, customer_client.id, customer_client.manager, customer_client.time_zone, customer_client.status FROM customer_client",
                    customer_id="123",
                ),
                call(
                    "SELECT customer_client.client_customer, customer_client.level, customer_client.id, customer_client.manager, customer_client.time_zone, customer_client.status FROM customer_client",
                    customer_id="789",
                ),
            ],
        ),  # Empty filter, expect all customers
        (
            ["active"],
            ["123", "789"],
            [
                call(
                    "SELECT customer_client.client_customer, customer_client.level, customer_client.id, customer_client.manager, customer_client.time_zone, customer_client.status FROM customer_client WHERE customer_client.status in ('active')",
                    customer_id="123",
                ),
                call(
                    "SELECT customer_client.client_customer, customer_client.level, customer_client.id, customer_client.manager, customer_client.time_zone, customer_client.status FROM customer_client WHERE customer_client.status in ('active')",
                    customer_id="789",
                ),
            ],
        ),  # Non-empty filter, expect filtered customers
    ],
)
def test_get_customers(config, mocker, customer_status_filter, expected_ids, send_request_calls):
    mock_google_api = Mock()

    mock_google_api.get_accessible_accounts.return_value = ["123", "789"]
    mock_google_api.send_request.side_effect = mock_send_request
    mock_google_api.parse_single_result.side_effect = lambda schema, result: result

    mock_config = {"customer_status_filter": customer_status_filter, "customer_ids": ["123", "456", "789"]}

    source = SourceGoogleAds(config, None, None)

    customers = source.get_customers(mock_google_api, mock_config)

    mock_google_api.send_request.assert_has_calls(send_request_calls)

    assert len(customers) == len(expected_ids)
    assert {customer.id for customer in customers} == set(expected_ids)


@pytest.mark.parametrize(
    "input_state, records_and_slices, expected",
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
def test_state_migration(input_state, records_and_slices, expected):
    # Create a fake customer_client_stream
    stream_mock = MagicMock()

    # Define what _read_parent_stream will yield
    stream_mock.stream_slices.return_value = (s for _, s in records_and_slices)

    def fake_read_records(stream_slice, sync_mode):
        return (r for r, s in records_and_slices if s == stream_slice)

    stream_mock.read_records.side_effect = fake_read_records

    migrator = GoogleAdsPerPartitionStateMigration(config=None, customer_client_stream=stream_mock)

    assert migrator.migrate(input_state) == expected


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
