#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from airbyte_cdk.models import SyncMode
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v8.errors.types.errors import ErrorCode, GoogleAdsError, GoogleAdsFailure
from google.ads.googleads.v8.errors.types.request_error import RequestErrorEnum
from grpc import RpcError
from source_google_ads.google_ads import GoogleAds
from source_google_ads.streams import ClickView

from .common import MockGoogleAdsClient as MockGoogleAdsClient


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


@pytest.fixture
def mock_ads_client(mocker):
    """Mock google ads library method, so it returns mocked Client"""
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.load_from_dict", return_value=MockGoogleAdsClient(test_config))


# EXPIRED_PAGE_TOKEN exception will be raised when page token has expired.
exception = GoogleAdsException(
    error=RpcError(),
    failure=GoogleAdsFailure(errors=[GoogleAdsError(error_code=ErrorCode(request_error=RequestErrorEnum.RequestError.EXPIRED_PAGE_TOKEN))]),
    call=RpcError(),
    request_id="test",
)


def mock_response_1():
    yield from [
        {"segments.date": "2021-01-01", "click_view.gclid": "1"},
        {"segments.date": "2021-01-02", "click_view.gclid": "2"},
        {"segments.date": "2021-01-03", "click_view.gclid": "3"},
        {"segments.date": "2021-01-03", "click_view.gclid": "4"},
    ]
    raise exception


def mock_response_2():
    yield from [
        {"segments.date": "2021-01-03", "click_view.gclid": "3"},
        {"segments.date": "2021-01-03", "click_view.gclid": "4"},
        {"segments.date": "2021-01-03", "click_view.gclid": "5"},
        {"segments.date": "2021-01-04", "click_view.gclid": "6"},
        {"segments.date": "2021-01-05", "click_view.gclid": "7"},
    ]


class MockGoogleAds(GoogleAds):
    count = 0

    def parse_single_result(self, schema, result):
        return result

    def send_request(self, query: str):
        self.count += 1
        if self.count == 1:
            return mock_response_1()
        else:
            return mock_response_2()


def test_page_token_expired_retry_succeeds(mock_ads_client, test_config):
    """
    Page token expired while reading records on date 2021-01-03
    The latest read record is {"segments.date": "2021-01-03", "click_view.gclid": "4"}
    It should retry reading starting from 2021-01-03, already read records will be reread again from that date.
    It shouldn't read records on 2021-01-01, 2021-01-02
    """
    stream_slice = {"start_date": "2021-01-01", "end_date": "2021-01-15"}

    google_api = MockGoogleAds(credentials=test_config["credentials"], customer_id=test_config["customer_id"])
    incremental_stream_config = dict(
        api=google_api,
        conversion_window_days=test_config["conversion_window_days"],
        start_date=test_config["start_date"],
        time_zone="local",
        end_date="2021-04-04",
    )
    stream = ClickView(**incremental_stream_config)
    stream.get_query = Mock()
    stream.get_query.return_value = "query"

    result = list(stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["segments.date"], stream_slice=stream_slice))
    assert len(result) == 9
    assert stream.get_query.call_count == 2
    stream.get_query.assert_called_with({"start_date": "2021-01-03", "end_date": "2021-01-15"})


def mock_response_fails_1():
    yield from [
        {"segments.date": "2021-01-01", "click_view.gclid": "1"},
        {"segments.date": "2021-01-02", "click_view.gclid": "2"},
        {"segments.date": "2021-01-03", "click_view.gclid": "3"},
        {"segments.date": "2021-01-03", "click_view.gclid": "4"},
    ]

    raise exception


def mock_response_fails_2():
    yield from [
        {"segments.date": "2021-01-03", "click_view.gclid": "3"},
        {"segments.date": "2021-01-03", "click_view.gclid": "4"},
        {"segments.date": "2021-01-03", "click_view.gclid": "5"},
        {"segments.date": "2021-01-03", "click_view.gclid": "6"},
    ]

    raise exception


class MockGoogleAdsFails(MockGoogleAds):
    def send_request(self, query: str):
        self.count += 1
        if self.count == 1:
            return mock_response_fails_1()
        else:
            return mock_response_fails_2()


def test_page_token_expired_retry_fails(mock_ads_client, test_config):
    """
    Page token has expired while reading records within date "2021-01-03", it should raise error,
    because Google Ads API doesn't allow filter by datetime.
    """
    stream_slice = {"start_date": "2021-01-01", "end_date": "2021-01-15"}

    google_api = MockGoogleAdsFails(credentials=test_config["credentials"], customer_id=test_config["customer_id"])
    incremental_stream_config = dict(
        api=google_api,
        conversion_window_days=test_config["conversion_window_days"],
        start_date=test_config["start_date"],
        time_zone="local",
        end_date="2021-04-04",
    )
    stream = ClickView(**incremental_stream_config)
    stream.get_query = Mock()
    stream.get_query.return_value = "query"

    with pytest.raises(GoogleAdsException):
        list(stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["segments.date"], stream_slice=stream_slice))

    stream.get_query.assert_called_with({"start_date": "2021-01-03", "end_date": "2021-01-15"})
    assert stream.get_query.call_count == 2


def mock_response_fails_one_date():
    yield from [
        {"segments.date": "2021-01-03", "click_view.gclid": "3"},
        {"segments.date": "2021-01-03", "click_view.gclid": "4"},
        {"segments.date": "2021-01-03", "click_view.gclid": "5"},
        {"segments.date": "2021-01-03", "click_view.gclid": "6"},
    ]

    raise exception


class MockGoogleAdsFailsOneDate(MockGoogleAds):
    def send_request(self, query: str):
        return mock_response_fails_one_date()


def test_page_token_expired_it_should_fail_date_range_1_day(mock_ads_client, test_config):
    """
    Page token has expired while reading records within date "2021-01-03",
    it should raise error, because Google Ads API doesn't allow filter by datetime.
    Minimum date range is 1 day.
    """
    stream_slice = {"start_date": "2021-01-03", "end_date": "2021-01-04"}

    google_api = MockGoogleAdsFailsOneDate(credentials=test_config["credentials"], customer_id=test_config["customer_id"])
    incremental_stream_config = dict(
        api=google_api,
        conversion_window_days=test_config["conversion_window_days"],
        start_date=test_config["start_date"],
        time_zone="local",
        end_date="2021-04-04",
    )
    stream = ClickView(**incremental_stream_config)
    stream.get_query = Mock()
    stream.get_query.return_value = "query"

    with pytest.raises(GoogleAdsException):
        list(stream.read_records(sync_mode=SyncMode.incremental, cursor_field=["segments.date"], stream_slice=stream_slice))

    stream.get_query.assert_called_with({"start_date": "2021-01-03", "end_date": "2021-01-04"})
    assert stream.get_query.call_count == 1
