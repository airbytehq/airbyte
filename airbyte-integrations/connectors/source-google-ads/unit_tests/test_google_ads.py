#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from datetime import date

import pendulum
import pytest
from google.ads.googleads.v17.services.types.google_ads_service import GoogleAdsRow
from google.auth import exceptions
from source_google_ads.google_ads import GoogleAds
from source_google_ads.streams import chunk_date_range

from airbyte_cdk.utils import AirbyteTracedException

from .common import MockGoogleAdsClient, MockGoogleAdsService


SAMPLE_SCHEMA = {
    "properties": {
        "segment.date": {
            "type": ["null", "string"],
        }
    }
}


class MockedDateSegment:
    def __init__(self, date: str):
        self._mock_date = date

    def __getattr__(self, attr):
        if attr == "date":
            return date.fromisoformat(self._mock_date)
        return MockedDateSegment(self._mock_date)


SAMPLE_CONFIG = {
    "credentials": {
        "developer_token": "developer_token",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
    }
}


EXPECTED_CRED = {
    "developer_token": "developer_token",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "refresh_token": "refresh_token",
    "use_proto_plus": True,
}


def test_google_ads_init(mocker):
    google_client_mocker = mocker.patch("source_google_ads.google_ads.GoogleAdsClient", return_value=MockGoogleAdsClient)
    _ = GoogleAds(**SAMPLE_CONFIG)
    assert google_client_mocker.load_from_dict.call_args[0][0] == EXPECTED_CRED


def test_google_ads_wrong_permissions(mocker):
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.load_from_dict", side_effect=exceptions.RefreshError("invalid_grant"))
    with pytest.raises(AirbyteTracedException) as e:
        GoogleAds(**SAMPLE_CONFIG)
    expected_message = "The authentication to Google Ads has expired. Re-authenticate to restore access to Google Ads."
    assert e.value.message == expected_message


def test_send_request(mocker, customers):
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.load_from_dict", return_value=MockGoogleAdsClient(SAMPLE_CONFIG))
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.get_service", return_value=MockGoogleAdsService())
    google_ads_client = GoogleAds(**SAMPLE_CONFIG)
    query = "Query"
    customer_id = next(iter(customers)).id
    response = list(google_ads_client.send_request(query, customer_id=customer_id))

    assert response[0].customer_id == customer_id
    assert response[0].query == query


def test_get_fields_from_schema():
    response = GoogleAds.get_fields_from_schema(SAMPLE_SCHEMA)
    assert response == ["segment.date"]


def test_interval_chunking():
    mock_intervals = [
        {"start_date": "2021-06-17", "end_date": "2021-06-26"},
        {"start_date": "2021-06-27", "end_date": "2021-07-06"},
        {"start_date": "2021-07-07", "end_date": "2021-07-16"},
        {"start_date": "2021-07-17", "end_date": "2021-07-26"},
        {"start_date": "2021-07-27", "end_date": "2021-08-05"},
        {"start_date": "2021-08-06", "end_date": "2021-08-10"},
    ]
    intervals = list(
        chunk_date_range(
            start_date="2021-07-01", end_date="2021-08-10", conversion_window=14, slice_duration=pendulum.Duration(days=9), time_zone="UTC"
        )
    )
    assert mock_intervals == intervals


generic_schema = {"properties": {"ad_group_id": {}, "segments.date": {}, "campaign_id": {}, "account_id": {}}}


@pytest.mark.parametrize(
    "fields, table_name, conditions, order_field, limit, expected_sql",
    (
        # Basic test case
        (
            ["ad_group_id", "segments.date", "campaign_id", "account_id"],
            "ad_group_ad",
            ["segments.date >= '2020-01-01'", "segments.date <= '2020-01-10'"],
            "segments.date",
            None,
            "SELECT ad_group_id, segments.date, campaign_id, account_id FROM ad_group_ad WHERE segments.date >= '2020-01-01' AND segments.date <= '2020-01-10' ORDER BY segments.date ASC",
        ),
        # Test with no conditions
        (
            ["ad_group_id", "segments.date", "campaign_id", "account_id"],
            "ad_group_ad",
            None,
            None,
            None,
            "SELECT ad_group_id, segments.date, campaign_id, account_id FROM ad_group_ad",
        ),
        # Test order with limit
        (
            ["ad_group_id", "segments.date", "campaign_id", "account_id"],
            "click_view",
            None,
            "ad_group_id",
            5,
            "SELECT ad_group_id, segments.date, campaign_id, account_id FROM click_view ORDER BY ad_group_id ASC LIMIT 5",
        ),
    ),
)
def test_convert_schema_into_query(fields, table_name, conditions, order_field, limit, expected_sql):
    query = GoogleAds.convert_schema_into_query(fields, table_name, conditions, order_field, limit)
    assert query == expected_sql


def test_get_field_value():
    field = "segment.date"
    date = "2001-01-01"
    response = GoogleAds.get_field_value(MockedDateSegment(date), field, {})
    assert response == date


def test_get_field_value_object():
    expected_response = [
        {"text": "An exciting headline", "policySummaryInfo": {"reviewStatus": "REVIEWED", "approvalStatus": "APPROVED"}},
        {"text": "second"},
    ]
    field = "ad_group_ad.ad.responsive_search_ad.headlines"
    ads_row = GoogleAdsRow(
        ad_group_ad={
            "ad": {
                "responsive_search_ad": {
                    "headlines": [
                        {
                            "text": "An exciting headline",
                            "policy_summary_info": {"review_status": "REVIEWED", "approval_status": "APPROVED"},
                        },
                        {"text": "second"},
                    ]
                }
            }
        }
    )

    response = GoogleAds.get_field_value(ads_row, field, {})
    assert [json.loads(i) for i in response] == expected_response


def test_get_field_value_strings():
    expected_response = [
        "http://url_one.com",
        "https://url_two.com",
    ]
    ads_row = GoogleAdsRow(
        ad_group_ad={
            "ad": {
                "final_urls": [
                    "http://url_one.com",
                    "https://url_two.com",
                ]
            }
        }
    )
    field = "ad_group_ad.ad.final_urls"
    response = GoogleAds.get_field_value(ads_row, field, {})
    assert response == expected_response


def test_parse_single_result():
    date = "2001-01-01"
    response = GoogleAds.parse_single_result(SAMPLE_SCHEMA, MockedDateSegment(date))
    assert response == response


def test_get_fields_metadata(mocker):
    # Mock the GoogleAdsClient to return our mock client
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient", MockGoogleAdsClient)

    # Instantiate the GoogleAds client
    google_ads_client = GoogleAds(**SAMPLE_CONFIG)

    # Define the fields we want metadata for
    fields = ["field1", "field2", "field3"]

    # Call the method to get fields metadata
    response = google_ads_client.get_fields_metadata(fields)

    # Get the mock service to check the request query
    mock_service = google_ads_client.get_client().get_service("GoogleAdsFieldService")

    # Assert the constructed request query
    expected_query = """
        SELECT
          name,
          data_type,
          enum_values,
          is_repeated
        WHERE name in ('field1','field2','field3')
        """
    assert mock_service.request_query.strip() == expected_query.strip()

    # Assert the response
    assert set(response.keys()) == set(fields)
    for field in fields:
        assert response[field].name == field
