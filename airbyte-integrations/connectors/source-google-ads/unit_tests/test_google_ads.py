#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import date

import pendulum
import pytest
from airbyte_cdk.utils import AirbyteTracedException
from freezegun import freeze_time
from google.auth import exceptions
from pendulum.tz.timezone import Timezone
from source_google_ads.google_ads import GoogleAds
from source_google_ads.models import Customer
from source_google_ads.streams import IncrementalGoogleAdsStream, chunk_date_range, get_date_params

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
        {"start_date": "2021-06-18", "end_date": "2021-06-27"},
        {"start_date": "2021-06-28", "end_date": "2021-07-07"},
        {"start_date": "2021-07-08", "end_date": "2021-07-17"},
        {"start_date": "2021-07-18", "end_date": "2021-07-27"},
        {"start_date": "2021-07-28", "end_date": "2021-08-06"},
        {"start_date": "2021-08-07", "end_date": "2021-08-15"},
    ]
    intervals = chunk_date_range("2021-07-01", 14, "segments.date", "2021-08-15", range_days=10)

    assert mock_intervals == intervals


def test_get_date_params(customers):
    # Please note that this is equal to inputted stream_slice start date + 1 day
    mock_start_date = "2021-05-19"
    mock_end_date = "2021-06-02"
    mock_conversion_window_days = 14

    incremental_stream_config = dict(
        conversion_window_days=mock_conversion_window_days,
        start_date=mock_start_date,
        api=MockGoogleAdsClient(SAMPLE_CONFIG),
        customers=customers,
    )

    stream = IncrementalGoogleAdsStream(**incremental_stream_config)

    for customer in stream.customers:
        start_date, end_date = get_date_params(
            start_date="2021-05-18", range_days=stream.range_days, time_zone=customer.time_zone, end_date=pendulum.parse("2021-08-15")
        )

        assert mock_start_date == start_date and mock_end_date == end_date


@freeze_time("2022-01-30 03:21:34", tz_offset=0)
def test_get_date_params_with_time_zone():
    time_zone_chatham = Timezone("Pacific/Chatham")  # UTC+12:45
    customer = Customer(id="id", time_zone=time_zone_chatham, is_manager_account=False)
    mock_start_date_chatham = pendulum.today(tz=time_zone_chatham).subtract(days=1).to_date_string()
    time_zone_honolulu = Timezone("Pacific/Honolulu")  # UTC-10:00
    customer_2 = Customer(id="id_2", time_zone=time_zone_honolulu, is_manager_account=False)
    mock_start_date_honolulu = pendulum.today(tz=time_zone_honolulu).subtract(days=1).to_date_string()

    mock_conversion_window_days = 14

    incremental_stream_config = dict(
        conversion_window_days=mock_conversion_window_days,
        start_date=mock_start_date_chatham,
        api=MockGoogleAdsClient(SAMPLE_CONFIG),
        customers=[customer],
    )
    stream = IncrementalGoogleAdsStream(**incremental_stream_config)
    start_date_chatham, end_date_chatham = get_date_params(
        start_date=mock_start_date_chatham, time_zone=customer.time_zone, range_days=stream.range_days
    )

    incremental_stream_config.update({"start_date": mock_start_date_honolulu, "customers": [customer_2]})
    stream_2 = IncrementalGoogleAdsStream(**incremental_stream_config)

    start_date_honolulu, end_date_honolulu = get_date_params(
        start_date=mock_start_date_honolulu, time_zone=customer_2.time_zone, range_days=stream_2.range_days
    )

    assert start_date_honolulu != start_date_chatham and end_date_honolulu != end_date_chatham


def test_convert_schema_into_query():
    report_name = "ad_group_ad_report"
    query = "SELECT segment.date FROM ad_group_ad WHERE segments.date >= '2020-01-01' AND segments.date <= '2020-03-01' ORDER BY segments.date ASC"
    response = GoogleAds.convert_schema_into_query(SAMPLE_SCHEMA, report_name, "2020-01-01", "2020-03-01", "segments.date")
    assert response == query


def test_get_field_value():
    field = "segment.date"
    date = "2001-01-01"
    response = GoogleAds.get_field_value(MockedDateSegment(date), field, {})
    assert response == date


def test_parse_single_result():
    date = "2001-01-01"
    response = GoogleAds.parse_single_result(SAMPLE_SCHEMA, MockedDateSegment(date))
    assert response == response


# Add a sample config with date parameters
SAMPLE_CONFIG_WITH_DATE = {
    "credentials": {
        "developer_token": "developer_token",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
    },
    "customer_id": "customer_id",
    "start_date": "2021-11-01",
    "end_date": "2021-11-15",
}


def test_get_date_params_with_date(customers):
    # Please note that this is equal to inputted stream_slice start date + 1 day
    mock_start_date = SAMPLE_CONFIG_WITH_DATE["start_date"]
    mock_end_date = SAMPLE_CONFIG_WITH_DATE["end_date"]
    incremental_stream_config = dict(
        start_date=mock_start_date,
        end_date=mock_end_date,
        conversion_window_days=0,
        customers=customers,
        api=MockGoogleAdsClient(SAMPLE_CONFIG_WITH_DATE),
    )
    stream = IncrementalGoogleAdsStream(**incremental_stream_config)
    for customer in stream.customers:
        start_date, end_date = get_date_params(
            start_date="2021-10-31", time_zone=customer.time_zone, range_days=stream.range_days, end_date=pendulum.parse("2021-11-15")
        )
        assert mock_start_date == start_date and mock_end_date == end_date


SAMPLE_CONFIG_WITHOUT_END_DATE = {
    "credentials": {
        "developer_token": "developer_token",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
    },
    "customer_id": "customer_id",
    "start_date": "2021-11-01",
}


def test_get_date_params_without_end_date(customers):
    # Please note that this is equal to inputted stream_slice start date + 1 day
    mock_start_date = SAMPLE_CONFIG_WITHOUT_END_DATE["start_date"]
    mock_end_date = "2021-11-30"
    incremental_stream_config = dict(
        start_date=mock_start_date,
        end_date=mock_end_date,
        conversion_window_days=0,
        customers=customers,
        api=MockGoogleAdsClient(SAMPLE_CONFIG_WITHOUT_END_DATE),
    )
    stream = IncrementalGoogleAdsStream(**incremental_stream_config)
    for customer in stream.customers:
        start_date, end_date = get_date_params(start_date="2021-10-31", range_days=stream.range_days, time_zone=customer.time_zone)
        assert mock_start_date == start_date
        # There is a Google limitation where we capture only a 15-day date range
        assert end_date == "2021-11-15"
