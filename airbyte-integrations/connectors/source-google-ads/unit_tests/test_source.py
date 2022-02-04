#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from freezegun import freeze_time
from source_google_ads.custom_query_stream import CustomQuery
from source_google_ads.google_ads import GoogleAds
from source_google_ads.source import SourceGoogleAds
from source_google_ads.streams import AdGroupAdReport, chunk_date_range


# Test chunck date range without end date
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
