#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import re
from collections import namedtuple
from unittest.mock import Mock, call

import pendulum
import pytest
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from pendulum import today
from source_google_ads.custom_query_stream import IncrementalCustomQuery
from source_google_ads.google_ads import GoogleAds
from source_google_ads.models import CustomerModel
from source_google_ads.source import SourceGoogleAds
from source_google_ads.streams import AdGroupAdLegacy, chunk_date_range
from source_google_ads.utils import GAQL

from .common import MockGoogleAdsClient


@pytest.fixture
def mock_get_customers(mocker):
    mocker.patch(
        "source_google_ads.source.SourceGoogleAds.get_customers",
        Mock(return_value=[CustomerModel(is_manager_account=False, time_zone="Europe/Berlin", id="8765")]),
    )


@pytest.fixture()
def stream_mock(mocker, config, customers):
    def mock(latest_record):
        mocker.patch("source_google_ads.streams.GoogleAdsStream.read_records", Mock(return_value=[latest_record]))
        google_api = GoogleAds(credentials=config["credentials"])
        client = AdGroupAdLegacy(
            start_date=config["start_date"], api=google_api, conversion_window_days=config["conversion_window_days"], customers=customers
        )
        return client

    return mock


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
    source = SourceGoogleAds()
    streams = source.streams(config)
    expected_streams_number = 30
    print(f"{config=} \n{streams=}")
    assert len(streams) == expected_streams_number


def test_read_missing_stream(config, mock_get_customers):
    source = SourceGoogleAds()

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

    try:
        list(source.read(logging.getLogger("airbyte"), config=config, catalog=catalog))
    except KeyError as error:
        pytest.fail(str(error))


@pytest.mark.parametrize(
    (
        "query",
        "is_metrics_in_query",
    ),
    (
        ("SELECT customer.id, metrics.conversions, campaign.start_date FROM campaign", True),
        ("SELECT segments.ad_destination_type, campaign.start_date, campaign.end_date FROM campaign", False),
    ),
)
def test_metrics_in_custom_query(query, is_metrics_in_query):
    source = SourceGoogleAds()
    assert source.is_metrics_in_custom_query(GAQL.parse(query)) is is_metrics_in_query


@pytest.mark.parametrize(
    ("latest_record", "current_state", "expected_state"),
    (
        ({"segments.date": "2020-01-01"}, {}, {"segments.date": "2020-01-01"}),
        ({"segments.date": "2020-02-01"}, {"segments.date": "2020-01-01"}, {"segments.date": "2020-02-01"}),
        ({"segments.date": "2021-03-03"}, {"1234567890": {"segments.date": "2020-02-01"}}, {"segments.date": "2021-03-03"}),
    ),
)
def test_updated_state(stream_mock, latest_record, current_state, expected_state):
    mocked_stream = stream_mock(latest_record=latest_record)
    mocked_stream.state = current_state
    for _ in mocked_stream.read_records(sync_mode=Mock(), stream_slice={"customer_id": "1234567890"}):
        pass
    assert mocked_stream.state["1234567890"] == expected_state


def stream_instance(query, api_mock, **kwargs):
    start_date = "2021-03-04"
    conversion_window_days = 14
    instance = IncrementalCustomQuery(
        api=api_mock,
        conversion_window_days=conversion_window_days,
        start_date=start_date,
        config={"query": GAQL.parse(query), "table_name": "whatever_table"},
        **kwargs,
    )
    return instance


@pytest.mark.parametrize(
    "original_query, expected_query",
    [
        (
            """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      metrics.impressions
    FROM campaign
    WHERE campaign.status = 'PAUSED'
    AND metrics.impressions > 100
    ORDER BY campaign.status
    """,
            """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      metrics.impressions,
      segments.date
    FROM campaign
    WHERE campaign.status = 'PAUSED'
    AND metrics.impressions > 100
     AND segments.date BETWEEN '1980-01-01' AND '2000-01-01'
    ORDER BY campaign.status
    """,
        ),
        (
            """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      metrics.impressions
    FROM campaign
    ORDER BY campaign.status
    """,
            """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      metrics.impressions,
      segments.date
    FROM campaign
    WHERE segments.date BETWEEN '1980-01-01' AND '2000-01-01'
    ORDER BY campaign.status
    """,
        ),
        (
            """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      metrics.impressions
    FROM campaign
    WHERE campaign.status = 'PAUSED'
    AND metrics.impressions > 100
    """,
            """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      metrics.impressions,
      segments.date
    FROM campaign
    WHERE campaign.status = 'PAUSED'
    AND metrics.impressions > 100
     AND segments.date BETWEEN '1980-01-01' AND '2000-01-01'
    """,
        ),
        (
            """
    SELECT
        campaign.accessible_bidding_strategy,
        segments.ad_destination_type,
        campaign.start_date,
        campaign.end_date
    FROM campaign
    """,
            """
    SELECT
        campaign.accessible_bidding_strategy,
        segments.ad_destination_type,
        campaign.start_date,
        campaign.end_date,
        segments.date
    FROM campaign
    WHERE segments.date BETWEEN '1980-01-01' AND '2000-01-01'
    """,
        ),
    ],
)
def test_insert_date(original_query, expected_query):
    expected_query = re.sub(r"\s+", " ", expected_query.strip())
    assert str(IncrementalCustomQuery.insert_segments_date_expr(GAQL.parse(original_query), "1980-01-01", "2000-01-01")) == expected_query


def test_get_json_schema_parse_query(mock_fields_meta_data, customers):
    query = """
        SELECT
            campaign.accessible_bidding_strategy,
            segments.ad_destination_type,
            campaign.start_date,
            campaign.end_date
        FROM campaign
        """
    final_fields = [
        "campaign.accessible_bidding_strategy",
        "segments.ad_destination_type",
        "campaign.start_date",
        "campaign.end_date",
        "segments.date",
    ]

    instance = stream_instance(query=query, api_mock=mock_fields_meta_data, customers=customers)
    final_schema = instance.get_json_schema()
    schema_keys = final_schema["properties"]
    assert set(schema_keys) == set(final_fields)  # test 1


# Test get json schema when start and end date are provided in the config file
def test_get_json_schema_parse_query_with_end_date(mock_fields_meta_data, customers):
    query = """
        SELECT
            campaign.accessible_bidding_strategy,
            segments.ad_destination_type,
            campaign.start_date,
            campaign.end_date
        FROM campaign
        """
    final_fields = [
        "campaign.accessible_bidding_strategy",
        "segments.ad_destination_type",
        "campaign.start_date",
        "campaign.end_date",
        "segments.date",
    ]

    instance = stream_instance(query=query, api_mock=mock_fields_meta_data, end_date="2021-04-04", customers=customers)
    final_schema = instance.get_json_schema()
    schema_keys = final_schema["properties"]
    assert set(schema_keys) == set(final_fields)  # test 1


def test_google_type_conversion(mock_fields_meta_data, customers):
    """
    query may be invalid (fields incompatibility did not checked).
    But we are just testing types, without submitting the query and further steps.
    Doing that with all possible types.
    """
    desired_mapping = {
        "accessible_bidding_strategy.target_impression_share.location": "string",  # "ENUM"
        "campaign.name": ["string", "null"],  # STRING
        "campaign.end_date": ["string", "null"],  # DATE
        "campaign.optimization_score": ["number", "null"],  # DOUBLE
        "campaign.resource_name": ["string", "null"],  # RESOURCE_NAME
        "campaign.shopping_setting.campaign_priority": ["integer", "null"],  # INT32
        "campaign.shopping_setting.merchant_id": ["integer", "null"],  # INT64
        "campaign_budget.explicitly_shared": ["boolean", "null"],  # BOOLEAN
        "bidding_strategy.enhanced_cpc": ["string", "null"],  # MESSAGE
        "segments.date": ["string", "null"],  # autoadded, should be DATE
    }

    # query is select field of each type
    query = """
        SELECT
            accessible_bidding_strategy.target_impression_share.location,
            campaign.name,
            campaign.end_date,
            campaign.optimization_score,
            campaign.resource_name,
            campaign.shopping_setting.campaign_priority,
            campaign.shopping_setting.merchant_id,
            campaign_budget.explicitly_shared,
            bidding_strategy.enhanced_cpc
        FROM campaign
        """
    instance = stream_instance(query=query, api_mock=mock_fields_meta_data, customers=customers)
    final_schema = instance.get_json_schema()
    schema_properties = final_schema.get("properties")
    for prop, value in schema_properties.items():
        assert desired_mapping[prop] == value.get("type"), f"{prop} should be {value}"


def test_check_connection_should_pass_when_config_valid(mocker):
    mocker.patch("source_google_ads.source.GoogleAds", MockGoogleAdsClient)
    source = SourceGoogleAds()
    check_successful, message = source.check_connection(
        logging.getLogger("airbyte"),
        {
            "credentials": {
                "developer_token": "fake_developer_token",
                "client_id": "fake_client_id",
                "client_secret": "fake_client_secret",
                "refresh_token": "fake_refresh_token",
            },
            "customer_id": "fake_customer_id",
            "start_date": "2022-01-01",
            "conversion_window_days": 14,
            "custom_queries_array": [
                {
                    "query": "SELECT campaign.accessible_bidding_strategy, segments.ad_destination_type, campaign.start_date, campaign.end_date FROM campaign",
                    "primary_key": None,
                    "cursor_field": "campaign.start_date",
                    "table_name": "happytable",
                },
                {
                    "query": "SELECT segments.ad_destination_type, segments.ad_network_type, segments.day_of_week, customer.auto_tagging_enabled, customer.id, metrics.conversions, campaign.start_date FROM campaign",
                    "primary_key": "customer.id",
                    "cursor_field": None,
                    "table_name": "unhappytable",
                },
                {
                    "query": "SELECT ad_group.targeting_setting.target_restrictions FROM ad_group",
                    "primary_key": "customer.id",
                    "cursor_field": None,
                    "table_name": "ad_group_custom",
                },
            ],
        },
    )
    assert check_successful
    assert message is None


def test_end_date_is_not_in_the_future(customers):
    source = SourceGoogleAds()
    config = source.get_incremental_stream_config(
        None, {"end_date": today().add(days=1).to_date_string(), "conversion_window_days": 14, "start_date": "2020-01-23"}, customers
    )
    assert config.get("end_date") == today().to_date_string()


def test_stream_slices(config, customers):
    google_api = GoogleAds(credentials=config["credentials"])
    stream = AdGroupAdLegacy(
        start_date=config["start_date"],
        api=google_api,
        conversion_window_days=config["conversion_window_days"],
        customers=customers,
        end_date="2021-02-10",
    )
    slices = list(stream.stream_slices())
    assert slices == [
        {"start_date": "2020-12-18", "end_date": "2021-01-01", "customer_id": "123", "login_customer_id": None},
        {"start_date": "2021-01-02", "end_date": "2021-01-16", "customer_id": "123", "login_customer_id": None},
        {"start_date": "2021-01-17", "end_date": "2021-01-31", "customer_id": "123", "login_customer_id": None},
        {"start_date": "2021-02-01", "end_date": "2021-02-10", "customer_id": "123", "login_customer_id": None},
    ]


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
def test_get_customers(mocker, customer_status_filter, expected_ids, send_request_calls):
    mock_google_api = Mock()

    mock_google_api.get_accessible_accounts.return_value = ["123", "789"]
    mock_google_api.send_request.side_effect = mock_send_request
    mock_google_api.parse_single_result.side_effect = lambda schema, result: result

    mock_config = {"customer_status_filter": customer_status_filter, "customer_ids": ["123", "456", "789"]}

    source = SourceGoogleAds()

    customers = source.get_customers(mock_google_api, mock_config)

    mock_google_api.send_request.assert_has_calls(send_request_calls)

    assert len(customers) == len(expected_ids)
    assert {customer.id for customer in customers} == set(expected_ids)
