#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import pytest
from source_google_ads.custom_query_stream import CustomQuery
from source_google_ads.google_ads import GoogleAds
from source_google_ads.streams import AdGroupAdReport, chunk_date_range


def test_chunk_date_range():
    start_date = "2021-03-04"
    end_date = "2021-05-04"
    conversion_window = 14
    field = "date"
    response = chunk_date_range(start_date, conversion_window, field, end_date)
    assert [{"date": "2021-02-18"}, {"date": "2021-03-18"}, {"date": "2021-04-18"}] == response


# this requires the config because instantiating a stream creates a google client. TODO refactor so client can be mocked.
def test_get_updated_state(config):
    google_api = GoogleAds(credentials=config["credentials"], customer_id=config["customer_id"])
    client = AdGroupAdReport(start_date=config["start_date"], api=google_api, conversion_window_days=config["conversion_window_days"])
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
