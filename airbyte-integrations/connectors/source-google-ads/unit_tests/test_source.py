#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from collections import namedtuple
from unittest.mock import Mock

import pytest
from airbyte_cdk import AirbyteLogger
from freezegun import freeze_time
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v11.errors.types.authorization_error import AuthorizationErrorEnum
from pendulum import today
from source_google_ads.custom_query_stream import CustomQuery
from source_google_ads.google_ads import GoogleAds
from source_google_ads.source import SourceGoogleAds
from source_google_ads.streams import AdGroupAdReport, AdGroupLabels, ServiceAccounts, chunk_date_range

from .common import MockErroringGoogleAdsClient, MockGoogleAdsClient, make_google_ads_exception


@pytest.fixture
def mock_account_info(mocker):
    mocker.patch(
        "source_google_ads.source.SourceGoogleAds.get_account_info",
        Mock(return_value=[[{"customer.manager": False, "customer.time_zone": "Europe/Berlin", "customer.id": "8765"}]]),
    )


@pytest.fixture()
def stream_mock(mocker, config, customers):
    def mock(latest_record):
        mocker.patch("source_google_ads.streams.GoogleAdsStream.read_records", Mock(return_value=[latest_record]))
        google_api = GoogleAds(credentials=config["credentials"])
        client = AdGroupAdReport(
            start_date=config["start_date"], api=google_api, conversion_window_days=config["conversion_window_days"], customers=customers
        )
        return client

    return mock


@pytest.fixture
def mocked_gads_api(mocker):
    def mock(response=None, failure_code=1, failure_msg="", error_type=""):
        def side_effect_func():
            raise make_google_ads_exception(failure_code=failure_code, failure_msg=failure_msg, error_type=error_type)
            yield

        side_effect = []
        if response:
            side_effect.append(response)
        if failure_msg or failure_code or error_type:
            side_effect.append(side_effect_func())
        mocker.patch("source_google_ads.google_ads.GoogleAds.send_request", side_effect=side_effect)

    return mock


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
        {"start_date": "2021-04-30", "end_date": "2021-05-04"},
    ] == response


def test_streams_count(config, mock_account_info):
    source = SourceGoogleAds()
    streams = source.streams(config)
    expected_streams_number = 19
    assert len(streams) == expected_streams_number


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
    instance = CustomQuery(
        api=api_mock,
        conversion_window_days=conversion_window_days,
        start_date=start_date,
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
    assert message.startswith("Unable to connect to Google Ads API with the provided configuration")


def test_end_date_is_not_in_the_future(customers):
    source = SourceGoogleAds()
    config = source.get_incremental_stream_config(
        None, {"end_date": today().add(days=1).to_date_string(), "conversion_window_days": 14, "start_date": "2020-01-23"}, customers
    )
    assert config.get("end_date") == today().to_date_string()


def test_invalid_custom_query_handled(mocked_gads_api, config):
    # limit to one custom query, otherwise need to mock more side effects
    config["custom_queries"] = [next(iter(config["custom_queries"]))]
    mocked_gads_api(
        response=[{"customer.id": "8765"}],
        failure_msg="Unrecognized field in the query: 'ad_group_ad.ad.video_ad.media_file'",
        error_type="request_error",
    )
    source = SourceGoogleAds()
    status_ok, error = source.check_connection(AirbyteLogger(), config)
    assert not status_ok
    assert error == (
        "Unable to connect to Google Ads API with the provided configuration - Unrecognized field in the query: "
        "'ad_group_ad.ad.video_ad.media_file'"
    )


@pytest.mark.parametrize(
    ("cls", "error", "failure_code", "raise_expected"),
    (
        (AdGroupLabels, "authorization_error", AuthorizationErrorEnum.AuthorizationError.CUSTOMER_NOT_ENABLED, False),
        (AdGroupLabels, "internal_error", 1, True),
        (ServiceAccounts, "authentication_error", 1, True),
        (ServiceAccounts, "internal_error", 1, True),
    ),
)
def test_read_record_error_handling(config, customers, caplog, mocked_gads_api, cls, error, failure_code, raise_expected):
    error_msg = "Some unexpected error"
    mocked_gads_api(failure_code=failure_code, failure_msg=error_msg, error_type=error)
    google_api = GoogleAds(credentials=config["credentials"])
    stream = cls(api=google_api, customers=customers)
    if raise_expected:
        with pytest.raises(GoogleAdsException):
            for _ in stream.read_records(sync_mode=Mock(), stream_slice={"customer_id": "1234567890"}):
                pass
    else:
        for _ in stream.read_records(sync_mode=Mock(), stream_slice={"customer_id": "1234567890"}):
            pass


def test_stream_slices(config, customers):
    google_api = GoogleAds(credentials=config["credentials"])
    stream = AdGroupAdReport(
        start_date=config["start_date"],
        api=google_api,
        conversion_window_days=config["conversion_window_days"],
        customers=customers,
        end_date="2021-02-10",
    )
    slices = list(stream.stream_slices())
    assert slices == [
        {"start_date": "2020-12-19", "end_date": "2021-01-02", "customer_id": "123"},
        {"start_date": "2021-01-03", "end_date": "2021-01-17", "customer_id": "123"},
        {"start_date": "2021-01-18", "end_date": "2021-02-01", "customer_id": "123"},
        {"start_date": "2021-02-02", "end_date": "2021-02-10", "customer_id": "123"},
    ]
