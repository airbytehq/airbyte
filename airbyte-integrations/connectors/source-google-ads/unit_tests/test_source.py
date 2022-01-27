#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import Mock

import pendulum
import pytest
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConfiguredAirbyteCatalog, Type
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v6.errors.types.errors import ErrorCode, GoogleAdsError, GoogleAdsFailure
from google.ads.googleads.v6.errors.types.request_error import RequestErrorEnum
from grpc import RpcError
from source_google_ads.custom_query_stream import CustomQuery
from source_google_ads.google_ads import GoogleAds
from source_google_ads.source import SourceGoogleAds
from source_google_ads.streams import AdGroupAdReport, ClickView, chunk_date_range
from .common import MockGoogleAdsClient as MockGoogleAdsClientBase


# Test chunck date range without end date
def test_chunk_date_range_without_end_date():
    start_date_str = pendulum.now().subtract(days=5).to_date_string()
    conversion_window = 0
    field = "date"
    response = chunk_date_range(
        start_date=start_date_str, conversion_window=conversion_window, field=field, end_date=None, days_of_data_storage=None, range_days=1
    )
    start_date = pendulum.parse(start_date_str)
    expected_response = []
    while start_date < pendulum.now():
        expected_response.append({field: start_date.to_date_string()})
        start_date = start_date.add(days=1)
    assert expected_response == response


def test_chunk_date_range():
    start_date = "2021-03-04"
    end_date = "2021-05-04"
    conversion_window = 14
    field = "date"
    response = chunk_date_range(start_date, conversion_window, field, end_date, range_days=10)
    assert [
        {"date": "2021-02-18"},
        {"date": "2021-02-28"},
        {"date": "2021-03-10"},
        {"date": "2021-03-20"},
        {"date": "2021-03-30"},
        {"date": "2021-04-09"},
        {"date": "2021-04-19"},
        {"date": "2021-04-29"},
    ] == response


def test_streams_count(config):
    source = SourceGoogleAds()
    streams = source.streams(config)
    expected_streams_number = 16
    assert len(streams) == expected_streams_number


def test_non_manager_account():
    mock_account_info = {"customer.manager": False}
    source = SourceGoogleAds()
    is_manager_account = source.is_manager_account(mock_account_info)
    assert not is_manager_account


def test_manager_account():
    mock_account_info = {"customer.manager": True}
    source = SourceGoogleAds()
    is_manager_account = source.is_manager_account(mock_account_info)
    assert is_manager_account


def test_metrics_in_custom_query():
    mock_query = "SELECT customer.id, metrics.conversions, campaign.start_date FROM campaign"
    source = SourceGoogleAds()
    is_metrics_in_custom_query = source.is_metrics_in_custom_query(mock_query)
    assert is_metrics_in_custom_query


def test_metrics_not_in_custom_query():
    mock_query = "SELECT segments.ad_destination_type, campaign.start_date, campaign.end_date FROM campaign"
    source = SourceGoogleAds()
    is_metrics_in_custom_query = source.is_metrics_in_custom_query(mock_query)
    assert not is_metrics_in_custom_query


def test_time_zone():
    mock_account_info = {}
    source = SourceGoogleAds()
    time_zone = source.get_time_zone(mock_account_info)
    assert time_zone == "local"


# this requires the config because instantiating a stream creates a google client. TODO refactor so client can be mocked.
def test_get_updated_state(config):
    google_api = GoogleAds(credentials=config["credentials"], customer_id=config["customer_id"])
    client = AdGroupAdReport(
        start_date=config["start_date"], api=google_api, conversion_window_days=config["conversion_window_days"], time_zone="local"
    )
    current_state_stream = {}
    latest_record = {"segments.date": "2020-01-01"}

    new_stream_state = client.get_updated_state(current_state_stream, latest_record)
    assert new_stream_state == {"segments.date": "2020-01-01"}

    current_state_stream = {"segments.date": "2020-01-01"}
    latest_record = {"segments.date": "2020-02-01"}
    new_stream_state = client.get_updated_state(current_state_stream, latest_record)
    assert new_stream_state == {"segments.date": "2020-02-01"}


def get_instance_from_config(config, query):
    start_date = "2021-03-04"
    conversion_window_days = 14
    google_api = GoogleAds(credentials=config["credentials"], customer_id=config["customer_id"])

    instance = CustomQuery(
        api=google_api,
        conversion_window_days=conversion_window_days,
        start_date=start_date,
        custom_query_config={"query": query, "table_name": "whatever_table"},
        time_zone="local",
    )
    return instance


# get he instance with a config
def get_instance_from_config_with_end_date(config, query):
    start_date = "2021-03-04"
    end_date = "2021-04-04"
    conversion_window_days = 14
    google_api = GoogleAds(credentials=config["credentials"], customer_id=config["customer_id"])

    instance = CustomQuery(
        api=google_api,
        conversion_window_days=conversion_window_days,
        start_date=start_date,
        end_date=end_date,
        time_zone="local",
        custom_query_config={"query": query, "table_name": "whatever_table"},
    )
    return instance


@pytest.mark.parametrize(
    "query, fields",
    [
        (
            """
    SELecT
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions FROM campaign
wheRe campaign.status = 'PAUSED'
AND metrics.impressions > 100
order by campaign.status
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
SELect
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions FROM campaign
wheRe campaign.status = 'PAUSED'
AND metrics.impressions > 100
order by campaign.status
""",
            """
SELect
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions , segments.date
FROM campaign
wheRe campaign.status = 'PAUSED'
AND metrics.impressions > 100
 AND segments.date BETWEEN '1980-01-01' AND '2000-01-01'
order by campaign.status
""",
        ),
        (
            """
SELect
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions
FROM campaign
order by campaign.status
""",
            """
SELect
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions
, segments.date
FROM campaign

WHERE segments.date BETWEEN '1980-01-01' AND '2000-01-01'
order by campaign.status
""",
        ),
        (
            """
SELect
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions FROM campaign
wheRe campaign.status = 'PAUSED'
AND metrics.impressions > 100
""",
            """
SELect
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions , segments.date
FROM campaign
wheRe campaign.status = 'PAUSED'
AND metrics.impressions > 100
 AND segments.date BETWEEN '1980-01-01' AND '2000-01-01'
""",
        ),
        (
            "SELECT campaign.accessible_bidding_strategy, segments.ad_destination_type, campaign.start_date, campaign.end_date FROM campaign",
            """SELECT campaign.accessible_bidding_strategy, segments.ad_destination_type, campaign.start_date, campaign.end_date , segments.date
FROM campaign
WHERE segments.date BETWEEN '1980-01-01' AND '2000-01-01'
""",
        ),
    ],
)
def test_insert_date(original_query, expected_query):
    assert CustomQuery.insert_segments_date_expr(original_query, "1980-01-01", "2000-01-01") == expected_query


def test_get_json_schema_parse_query(config):
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

    instance = get_instance_from_config(config=config, query=query)
    final_schema = instance.get_json_schema()
    schema_keys = final_schema["properties"]
    assert set(schema_keys) == set(final_fields)  # test 1


# Test get json schema when start and end date are provided in the config file
def test_get_json_schema_parse_query_with_end_date(config):
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

    instance = get_instance_from_config_with_end_date(config=config, query=query)
    final_schema = instance.get_json_schema()
    schema_keys = final_schema["properties"]
    assert set(schema_keys) == set(final_fields)  # test 1


def test_google_type_conversion(config):
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
    instance = get_instance_from_config(config=config, query=query)
    final_schema = instance.get_json_schema()
    schema_properties = final_schema.get("properties")
    for prop, value in schema_properties.items():
        assert desired_mapping[prop] == value.get("type"), f"{prop} should be {value}"


class MockErrorResponse:
    def __iter__(self):
        return self

    def __next__(self):
        e = GoogleAdsException(
            error=RpcError(),
            failure=GoogleAdsFailure(
                errors=[GoogleAdsError(error_code=ErrorCode(request_error=RequestErrorEnum.RequestError.EXPIRED_PAGE_TOKEN))]
            ),
            call=RpcError(),
            request_id="test",
        )
        raise e


class MockGoogleAdsService:
    count = 0

    def search(self, search_request):
        self.count += 1
        if self.count == 1:
            # For the first attempt (with date range = 15 days) return Error Response
            return MockErrorResponse()
        else:
            # the second attempt should succeed, (date range = 7 days)
            # this payload is dummy, in this case test stream records will be printed with None values in all fields.
            return [{"id": 1}, {"id": 2}]


class MockGoogleAdsServiceWhichFails:
    def search(self, search_request):
        # For all attempts, return Error Response
        return MockErrorResponse()


class MockGoogleAdsClient(MockGoogleAdsClientBase):
    def get_service(self, service):
        return MockGoogleAdsService()


class MockGoogleAdsClientWhichFails(MockGoogleAdsClientBase):
    def get_service(self, service):
        return MockGoogleAdsServiceWhichFails()


@pytest.fixture(scope="module")
def configured_catalog():
    with open("unit_tests/configured_catalog.json") as f:
        data = json.loads(f.read())
    return ConfiguredAirbyteCatalog.parse_obj(data)


@pytest.fixture(scope="module")
def test_config():
    config = {
        "credentials": {
            "developer_token": "test_token",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
        },
        "customer_id": "123",
        "start_date": "2021-01-01",
        "conversion_window_days": 14,
    }
    return config


@pytest.fixture()
def test_stream(test_config):
    google_api = GoogleAds(credentials=test_config["credentials"], customer_id=test_config["customer_id"])
    incremental_stream_config = dict(
        api=google_api,
        conversion_window_days=test_config["conversion_window_days"],
        start_date=test_config["start_date"],
        time_zone="local",
        end_date="2021-04-04",
    )
    stream = ClickView(**incremental_stream_config)
    stream.range_days = 15
    return stream


@pytest.fixture
def mock_ads_client(mocker):
    """Mock google ads library method, so it returns mocked Client"""
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.load_from_dict", return_value=MockGoogleAdsClient(test_config))


@pytest.fixture
def mock_ads_client_which_fails(mocker):
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.load_from_dict", return_value=MockGoogleAdsClientWhichFails(test_config))


def test_page_token_expired_retry_with_less_date_range_should_succeed(mock_ads_client, configured_catalog, test_config, test_stream):
    """Page token expired when date range is 15 days, reducing to 7 days succeeds"""

    source = SourceGoogleAds()
    source.streams = Mock()
    source.streams.return_value = [test_stream]
    logger = AirbyteLogger()

    assert test_stream.range_days == 15
    result = list(source.read(logger=logger, config=test_config, catalog=configured_catalog))
    assert test_stream.range_days == 7
    records = [item for item in result if item.type == Type.RECORD]
    assert len(records) == 2


def test_page_token_expired_should_fail(mock_ads_client_which_fails, configured_catalog, test_config, test_stream):
    """if Page token expired when date range is 1 day, it should fail."""
    source = SourceGoogleAds()
    source.streams = Mock()
    source.streams.return_value = [test_stream]
    logger = AirbyteLogger()

    assert test_stream.range_days == 15
    with pytest.raises(GoogleAdsException):
        list(source.read(logger=logger, config=test_config, catalog=configured_catalog))
    assert test_stream.range_days == 1
