#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import date

import pytest
from airbyte_cdk.utils import AirbyteTracedException
from google.auth import exceptions
from source_google_ads.google_ads import GoogleAds
from source_google_ads.streams import chunk_date_range

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
    page_size = 1000
    customer_id = next(iter(customers)).id
    response = list(google_ads_client.send_request(query, customer_id=customer_id))

    assert response[0].customer_id == customer_id
    assert response[0].query == query
    assert response[0].page_size == page_size


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
    intervals = list(chunk_date_range("2021-07-01", 14, "2021-08-10", range_days=10))
    assert mock_intervals == intervals


generic_schema = {"properties": {"ad_group_id": {}, "segments.date": {}, "campaign_id": {}, "account_id": {}}}


@pytest.mark.parametrize(
    "stream_schema, report_name, slice_start, slice_end, cursor, expected_sql",
    (
        (
            generic_schema,
            "ad_group_ads",
            "2020-01-01",
            "2020-01-10",
            "segments.date",
            "SELECT ad_group_id, segments.date, campaign_id, account_id FROM ad_group_ad WHERE segments.date >= '2020-01-01' AND segments.date <= '2020-01-10' ORDER BY segments.date ASC"
        ),
        (
            generic_schema,
            "ad_group_ads",
            "2020-01-01",
            "2020-01-02",
            "segments.date",
            "SELECT ad_group_id, segments.date, campaign_id, account_id FROM ad_group_ad WHERE segments.date >= '2020-01-01' AND segments.date <= '2020-01-02' ORDER BY segments.date ASC"
        ),
        (
            generic_schema,
            "ad_group_ads",
            None,
            None,
            None,
            "SELECT ad_group_id, segments.date, campaign_id, account_id FROM ad_group_ad"
        ),
        (
            generic_schema,
            "click_view",
            "2020-01-01",
            "2020-01-10",
            "segments.date",
            "SELECT ad_group_id, segments.date, campaign_id, account_id FROM click_view WHERE segments.date >= '2020-01-01' AND segments.date <= '2020-01-10' ORDER BY segments.date ASC"
        ),
        (
            generic_schema,
            "click_view",
            "2020-01-01",
            "2020-01-02",
            "segments.date",
            "SELECT ad_group_id, segments.date, campaign_id, account_id FROM click_view WHERE segments.date >= '2020-01-01' AND segments.date <= '2020-01-02' ORDER BY segments.date ASC"
        ),
        (
            generic_schema,
            "click_view",
            None,
            None,
            None,
            "SELECT ad_group_id, segments.date, campaign_id, account_id FROM click_view"
        ),
    ),
)
def test_convert_schema_into_query(stream_schema, report_name, slice_start, slice_end, cursor, expected_sql):
    query = GoogleAds.convert_schema_into_query(stream_schema, report_name, slice_start, slice_end, cursor)
    assert query == expected_sql


def test_get_field_value():
    field = "segment.date"
    date = "2001-01-01"
    response = GoogleAds.get_field_value(MockedDateSegment(date), field, {})
    assert response == date


def test_parse_single_result():
    date = "2001-01-01"
    response = GoogleAds.parse_single_result(SAMPLE_SCHEMA, MockedDateSegment(date))
    assert response == response
