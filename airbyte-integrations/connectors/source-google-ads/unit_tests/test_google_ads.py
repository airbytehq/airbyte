#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import date

import pendulum
from pendulum.tz.timezone import Timezone
from source_google_ads.google_ads import GoogleAds
from source_google_ads.streams import IncrementalGoogleAdsStream, chunk_date_range

SAMPLE_SCHEMA = {
    "properties": {
        "segment.date": {
            "type": ["null", "string"],
        }
    }
}


# Mocking Classes
class MockGoogleAdsService:
    def search(self, search_request):
        return search_request


class MockedDateSegment:
    def __init__(self, date: str):
        self._mock_date = date

    def __getattr__(self, attr):
        if attr == "date":
            return date.fromisoformat(self._mock_date)
        return MockedDateSegment(self._mock_date)


class MockSearchRequest:
    customer_id = "12345"
    query = None
    page_size = 100
    page_token = None


class MockGoogleAdsClient:
    def __init__(self, config):
        self.config = config

    def get_type(self, type):
        return MockSearchRequest()

    def get_service(self, service):
        return MockGoogleAdsService()

    @staticmethod
    def load_from_dict(config):
        return MockGoogleAdsClient(config)


SAMPLE_CONFIG = {
    "credentials": {
        "developer_token": "developer_token",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
    },
    "customer_id": "customer_id",
}

EXPECTED_CRED = {
    "developer_token": "developer_token",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "refresh_token": "refresh_token",
}


def test_google_ads_init(mocker):
    google_client_mocker = mocker.patch("source_google_ads.google_ads.GoogleAdsClient", return_value=MockGoogleAdsClient)
    google_ads_client = GoogleAds(**SAMPLE_CONFIG)
    assert google_ads_client.customer_id == SAMPLE_CONFIG["customer_id"]
    assert google_client_mocker.load_from_dict.call_args[0][0] == EXPECTED_CRED


def test_send_request(mocker):
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.load_from_dict", return_value=MockGoogleAdsClient(SAMPLE_CONFIG))
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.get_service", return_value=MockGoogleAdsService())
    google_ads_client = GoogleAds(**SAMPLE_CONFIG)
    query = "Query"
    page_size = 1000
    response = google_ads_client.send_request(query)

    assert response.customer_id == SAMPLE_CONFIG["customer_id"]
    assert response.query == query
    assert response.page_size == page_size


def test_get_fields_from_schema():
    response = GoogleAds.get_fields_from_schema(SAMPLE_SCHEMA)
    assert response == ["segment.date"]


def test_interval_chunking():
    mock_intervals = [{"segments.date": "2021-05-18"}, {"segments.date": "2021-06-18"}, {"segments.date": "2021-07-18"}]
    intervals = chunk_date_range("2021-06-01", 14, "segments.date", "2021-08-15")

    assert mock_intervals == intervals


def test_get_date_params():
    # Please note that this is equal to inputted stream_slice start date + 1 day
    mock_start_date = "2021-05-19"
    mock_end_date = "2021-06-18"
    mock_conversion_window_days = 14

    incremental_stream_config = dict(
        conversion_window_days=mock_conversion_window_days,
        start_date=mock_start_date,
        api=MockGoogleAdsClient(SAMPLE_CONFIG),
        time_zone="local",
    )

    start_date, end_date = IncrementalGoogleAdsStream(**incremental_stream_config).get_date_params(
        stream_slice={"segments.date": "2021-05-18"}, cursor_field="segments.date", end_date=pendulum.parse("2021-08-15")
    )

    assert mock_start_date == start_date and mock_end_date == end_date


def test_get_date_params_with_time_zone():
    time_zone_chatham = Timezone("Pacific/Chatham")  # UTC+12:45
    mock_start_date_chatham = pendulum.today(tz=time_zone_chatham).subtract(days=1).to_date_string()
    time_zone_honolulu = Timezone("Pacific/Honolulu")  # UTC-10:00
    mock_start_date_honolulu = pendulum.today(tz=time_zone_honolulu).subtract(days=1).to_date_string()

    mock_conversion_window_days = 14

    incremental_stream_config = dict(
        conversion_window_days=mock_conversion_window_days,
        start_date=mock_start_date_chatham,
        api=MockGoogleAdsClient(SAMPLE_CONFIG),
        time_zone=time_zone_chatham,
    )
    start_date_chatham, end_date_chatham = IncrementalGoogleAdsStream(**incremental_stream_config).get_date_params(
        stream_slice={"segments.date": mock_start_date_chatham}, cursor_field="segments.date"
    )

    incremental_stream_config.update({"start_date": mock_start_date_honolulu, "time_zone": time_zone_honolulu})
    start_date_honolulu, end_date_honolulu = IncrementalGoogleAdsStream(**incremental_stream_config).get_date_params(
        stream_slice={"segments.date": mock_start_date_honolulu}, cursor_field="segments.date"
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
