#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import Mock

import pytest
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.errors.types.errors import ErrorCode, GoogleAdsError, GoogleAdsFailure
from google.ads.googleads.v20.errors.types.request_error import RequestErrorEnum
from google.api_core.exceptions import (
    DataLoss,
    InternalServerError,
    ResourceExhausted,
    ServiceUnavailable,
    TooManyRequests,
    Unauthenticated,
)
from grpc import RpcError
from source_google_ads.google_ads import GoogleAds
from source_google_ads.streams import ServiceAccounts

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.utils import AirbyteTracedException


# EXPIRED_PAGE_TOKEN exception will be raised when page token has expired.
exception = GoogleAdsException(
    error=RpcError(),
    failure=GoogleAdsFailure(errors=[GoogleAdsError(error_code=ErrorCode(request_error=RequestErrorEnum.RequestError.EXPIRED_PAGE_TOKEN))]),
    call=RpcError(),
    request_id="test",
)


def mock_response_1():
    yield [
        {"segments.date": "2021-01-01", "click_view.gclid": "1"},
        {"segments.date": "2021-01-02", "click_view.gclid": "2"},
        {"segments.date": "2021-01-03", "click_view.gclid": "3"},
        {"segments.date": "2021-01-03", "click_view.gclid": "4"},
    ]
    raise exception


def mock_response_2():
    yield [
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

    def send_request(self, query: str, customer_id: str, login_customer_id: str = "none"):
        self.count += 1
        if self.count == 1:
            return mock_response_1()
        else:
            return mock_response_2()


def mock_response_fails_1():
    yield [
        {"segments.date": "2021-01-01", "click_view.gclid": "1"},
        {"segments.date": "2021-01-02", "click_view.gclid": "2"},
        {"segments.date": "2021-01-03", "click_view.gclid": "3"},
        {"segments.date": "2021-01-03", "click_view.gclid": "4"},
    ]

    raise exception


def mock_response_fails_2():
    yield [
        {"segments.date": "2021-01-03", "click_view.gclid": "3"},
        {"segments.date": "2021-01-03", "click_view.gclid": "4"},
        {"segments.date": "2021-01-03", "click_view.gclid": "5"},
        {"segments.date": "2021-01-03", "click_view.gclid": "6"},
    ]

    raise exception


class MockGoogleAdsFails(MockGoogleAds):
    def send_request(self, query: str, customer_id: str, login_customer_id: str = "none"):
        self.count += 1
        if self.count == 1:
            return mock_response_fails_1()
        else:
            return mock_response_fails_2()


def mock_response_fails_one_date():
    yield [
        {"segments.date": "2021-01-03", "click_view.gclid": "3"},
        {"segments.date": "2021-01-03", "click_view.gclid": "4"},
        {"segments.date": "2021-01-03", "click_view.gclid": "5"},
        {"segments.date": "2021-01-03", "click_view.gclid": "6"},
    ]

    raise exception


class MockGoogleAdsFailsOneDate(MockGoogleAds):
    def send_request(self, query: str, customer_id: str, login_customer_id: str = "none"):
        return mock_response_fails_one_date()


def test_read_records_unauthenticated(mocker, customers, config):
    credentials = config["credentials"]
    api = GoogleAds(credentials=credentials)

    mocker.patch.object(api, "parse_single_result", side_effect=Unauthenticated(message="Unauthenticated"))

    stream_config = dict(
        api=api,
        customers=customers,
    )
    stream = ServiceAccounts(**stream_config)
    with pytest.raises(AirbyteTracedException) as exc_info:
        list(stream.read_records(SyncMode.full_refresh, {"customer_id": "customer_id", "login_customer_id": "default"}))

    assert exc_info.value.message == (
        "Authentication failed for the customer 'customer_id'. Please try to Re-authenticate your credentials on set up Google Ads page."
    )
