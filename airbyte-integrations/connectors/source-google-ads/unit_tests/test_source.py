#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from collections import namedtuple
from unittest.mock import Mock

import pytest
from airbyte_cdk import AirbyteLogger
from freezegun import freeze_time
from pendulum import today
from source_google_ads.custom_query_stream import CustomQuery
from source_google_ads.google_ads import GoogleAds
from source_google_ads.source import SourceGoogleAds
from source_google_ads.streams import AdGroupAdReport, chunk_date_range

from .common import MockErroringGoogleAdsClient, MockGoogleAdsClient


@pytest.fixture
def mock_account_info(mocker):
    mocker.patch(
        "source_google_ads.source.SourceGoogleAds.get_account_info",
        Mock(return_value={"customer.manager": False, "customer.time_zone": "Europe/Berlin"}),
    )


@pytest.fixture()
def client_mock(config):
    google_api = GoogleAds(credentials=config["credentials"], customer_id=config["customer_id"])
    client = AdGroupAdReport(
        start_date=config["start_date"], api=google_api, conversion_window_days=config["conversion_window_days"], time_zone="local"
    )
    client._customer_id = "1234567890"
    return client


@pytest.fixture()
def mock_fields_meta_data():
    Node = namedtuple("Node", ["data_type", "name", "enum_values", "is_repeated"])
    nodes = (
        Node("RESOURCE_NAME", "campaign.accessible_bidding_strategy", [], False),
        Node(
            "ENUM",
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
        Node("DATE", "campaign.start_date", [], is_repeated=False),
        Node("DATE", "campaign.end_date", [], False),
        Node("DATE", "segments.date", [], False),
        Node(
            "ENUM",
            "accessible_bidding_strategy.target_impression_share.location",
            ["ABSOLUTE_TOP_OF_PAGE", "ANYWHERE_ON_PAGE", "TOP_OF_PAGE", "UNKNOWN", "UNSPECIFIED"],
            False,
        ),
        Node("STRING", "campaign.name", [], False),
        Node("DOUBLE", "campaign.optimization_score", [], False),
        Node("RESOURCE_NAME", "campaign.resource_name", [], False),
        Node("INT32", "campaign.shopping_setting.campaign_priority", [], False),
        Node("INT64", "campaign.shopping_setting.merchant_id", [], False),
        Node("BOOLEAN", "campaign_budget.explicitly_shared", [], False),
        Node("MESSAGE", "bidding_strategy.enhanced_cpc", [], False),
    )
    return Mock(get_fields_metadata=Mock(return_value={node.name: node for node in nodes}))


# Test chunk date range without end date
@freeze_time("2022-01-30")
def test_chunk_date_range_without_end_date():
    start_date_str = "2022-01-24"
    conversion_window = 0
    field = "date"
    response = chunk_date_range(
        start_date=start_date_str, conversion_window=conversion_window, field=field, end_date=None, days_of_data_storage=None, range_days=1
    )
    expected_response = [
        {"start_date": "2022-01-25", "end_date": "2022-01-26"},
        {"start_date": "2022-01-26", "end_date": "2022-01-27"},
        {"start_date": "2022-01-27", "end_date": "2022-01-28"},
        {"start_date": "2022-01-28", "end_date": "2022-01-29"},
        {"start_date": "2022-01-29", "end_date": "2022-01-30"},
        {"start_date": "2022-01-30", "end_date": "2022-01-31"},
    ]
    assert expected_response == response


def test_chunk_date_range():
    start_date = "2021-03-04"
    end_date = "2021-05-04"
    conversion_window = 14
    field = "date"
    response = chunk_date_range(start_date, conversion_window, field, end_date, range_days=10)
    assert [
        {"start_date": "2021-02-19", "end_date": "2021-02-28"},
        {"start_date": "2021-03-01", "end_date": "2021-03-10"},
        {"start_date": "2021-03-11", "end_date": "2021-03-20"},
        {"start_date": "2021-03-21", "end_date": "2021-03-30"},
        {"start_date": "2021-03-31", "end_date": "2021-04-09"},
        {"start_date": "2021-04-10", "end_date": "2021-04-19"},
        {"start_date": "2021-04-20", "end_date": "2021-04-29"},
        {"start_date": "2021-04-30", "end_date": "2021-05-09"},
    ] == response


def test_streams_count(config, mock_account_info):
    source = SourceGoogleAds()
    streams = source.streams(config)
    expected_streams_number = 19
    assert len(streams) == expected_streams_number


@pytest.mark.parametrize("is_manager_account", (True, False))
def test_manager_account(is_manager_account):
    mock_account_info = {"customer.manager": is_manager_account}
    source = SourceGoogleAds()
    assert source.is_manager_account(mock_account_info) is is_manager_account


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
    assert source.is_metrics_in_custom_query(query) is is_metrics_in_query


def test_time_zone():
    mock_account_info = {}
    source = SourceGoogleAds()
    time_zone = source.get_time_zone(mock_account_info)
    assert time_zone == "local"


def test_get_updated_state(client_mock):
    current_state_stream = {}
    latest_record = {"segments.date": "2020-01-01"}
    new_stream_state = client_mock.get_updated_state(current_state_stream, latest_record)
    assert new_stream_state == {"1234567890": {"segments.date": "2020-01-01"}}

    current_state_stream = {"segments.date": "2020-01-01"}
    latest_record = {"segments.date": "2020-02-01"}
    new_stream_state = client_mock.get_updated_state(current_state_stream, latest_record)
    assert new_stream_state == {"1234567890": {"segments.date": "2020-02-01"}}

    current_state_stream = {"1234567890": {"segments.date": "2020-02-01"}}
    latest_record = {"segments.date": "2021-03-03"}
    new_stream_state = client_mock.get_updated_state(current_state_stream, latest_record)
    assert new_stream_state == {"1234567890": {"segments.date": "2021-03-03"}}


def stream_instance(query, api_mock, **kwargs):
    start_date = "2021-03-04"
    conversion_window_days = 14
    instance = CustomQuery(
        api=api_mock,
        conversion_window_days=conversion_window_days,
        start_date=start_date,
        time_zone="local",
        custom_query_config={"query": query, "table_name": "whatever_table"},
        **kwargs,
    )
    return instance


@pytest.mark.parametrize(
    "query, fields",
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
            ["campaign.id", "campaign.name", "campaign.status", "metrics.impressions"],
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
            ["campaign.accessible_bidding_strategy", "segments.ad_destination_type", "campaign.start_date", "campaign.end_date"],
        ),
        ("""selet aasdasd from aaa""", []),
    ],
)
def test_get_query_fields(query, fields):
    assert CustomQuery.get_query_fields(query) == fields


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
  metrics.impressions
, segments.date
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
  metrics.impressions
, segments.date
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
  metrics.impressions
, segments.date
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
    campaign.end_date
, segments.date
FROM campaign

WHERE segments.date BETWEEN '1980-01-01' AND '2000-01-01'
""",
        ),
    ],
)
def test_insert_date(original_query, expected_query):
    assert CustomQuery.insert_segments_date_expr(original_query, "1980-01-01", "2000-01-01") == expected_query


def test_get_json_schema_parse_query(mock_fields_meta_data):
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

    instance = stream_instance(query=query, api_mock=mock_fields_meta_data)
    final_schema = instance.get_json_schema()
    schema_keys = final_schema["properties"]
    assert set(schema_keys) == set(final_fields)  # test 1


# Test get json schema when start and end date are provided in the config file
def test_get_json_schema_parse_query_with_end_date(mock_fields_meta_data):
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

    instance = stream_instance(query=query, api_mock=mock_fields_meta_data, end_date="2021-04-04")
    final_schema = instance.get_json_schema()
    schema_keys = final_schema["properties"]
    assert set(schema_keys) == set(final_fields)  # test 1


def test_google_type_conversion(mock_fields_meta_data):
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
    instance = stream_instance(query=query, api_mock=mock_fields_meta_data)
    final_schema = instance.get_json_schema()
    schema_properties = final_schema.get("properties")
    for prop, value in schema_properties.items():
        assert desired_mapping[prop] == value.get("type"), f"{prop} should be {value}"


def test_check_connection_should_pass_when_config_valid(mocker):
    mocker.patch("source_google_ads.source.GoogleAds", MockGoogleAdsClient)
    source = SourceGoogleAds()
    check_successful, message = source.check_connection(
        AirbyteLogger(),
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
            "custom_queries": [
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


def test_check_connection_should_fail_when_api_call_fails(mocker):
    # We patch the object inside source.py because that's the calling context
    # https://docs.python.org/3/library/unittest.mock.html#where-to-patch
    mocker.patch("source_google_ads.source.GoogleAds", MockErroringGoogleAdsClient)
    source = SourceGoogleAds()
    check_successful, message = source.check_connection(
        AirbyteLogger(),
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
            "custom_queries": [
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
    assert not check_successful
    assert message.startswith("Unable to connect to Google Ads API with the provided credentials")


def test_end_date_is_not_in_the_future():
    source = SourceGoogleAds()
    config = source.get_incremental_stream_config(
        None, {"end_date": today().add(days=1).to_date_string(), "conversion_window_days": 14, "start_date": "2020-01-23"}
    )
    assert config.get("end_date") == today().to_date_string()
