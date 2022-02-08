#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_impact_advertisers_report.source import MediaPartners
from airbyte_cdk.sources.streams.http.auth.core import NoAuth

DEFAULT_CONFIG = {
  "account_sid": "account_sid",
  "auth_token": "some_token",
  "report_id": "att_adv_performance_by_media_pm_only",
  "start_date": "2019-11-14",
  "sub_ad_id": "10732"
}

@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(MediaPartners, "path", "v0/example_endpoint")
    mocker.patch.object(MediaPartners, "primary_key", "test_primary_key")
    mocker.patch.object(MediaPartners, "__abstractmethods__", set())


def test_report_request_params(patch_base_class):
    stream = MediaPartners(
        authenticator=NoAuth,
        account_sid=DEFAULT_CONFIG["account_sid"],
        auth_token=DEFAULT_CONFIG["auth_token"],
        report_id=DEFAULT_CONFIG["report_id"],
        start_date=DEFAULT_CONFIG["start_date"],
        sub_ad_id=DEFAULT_CONFIG["sub_ad_id"]
    )
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {
        "Page": 1,
        "PageSize": 5000
    }
    assert stream.request_params(**inputs) == expected_params


def test_report_next_page_token(patch_base_class):
    stream = MediaPartners(
        authenticator=NoAuth,
        account_sid=DEFAULT_CONFIG["account_sid"],
        auth_token=DEFAULT_CONFIG["auth_token"],
        report_id=DEFAULT_CONFIG["report_id"],
        start_date=DEFAULT_CONFIG["start_date"],
        sub_ad_id=DEFAULT_CONFIG["sub_ad_id"]
    )

    response = MagicMock()
    response.json.return_value = {"@nextpageuri": f'/Advertisers/{DEFAULT_CONFIG["account_sid"]}/Reports/{DEFAULT_CONFIG["report_id"]}?PageSize=5000&Page=2&START_DATE={DEFAULT_CONFIG["start_date"]}&SUBAID={DEFAULT_CONFIG["sub_ad_id"]}'}
    inputs = {"response": response}

    expected_token = {"Page": "2", "PageSize": "5000", "START_DATE": "2019-11-14", "SUBAID": "10732"}
    assert stream.next_page_token(**inputs) == expected_token


def test_report_parse_response(patch_base_class):
    stream = MediaPartners(
        authenticator=NoAuth,
        account_sid=DEFAULT_CONFIG["account_sid"],
        auth_token=DEFAULT_CONFIG["auth_token"],
        report_id=DEFAULT_CONFIG["report_id"],
        start_date=DEFAULT_CONFIG["start_date"],
        sub_ad_id=DEFAULT_CONFIG["sub_ad_id"]
    )
    media_partners = [
        {"key": "value"},
        {"key": "value2"},
    ]
    response = MagicMock()
    response.json.return_value = {
        "@page": "1",
        "@numpages": "1",
        "@pagesize": "20000",
        "@total": "502",
        "@start": "0",
        "@end": "501",
        "@uri": f'/Advertisers/{DEFAULT_CONFIG["account_sid"]}/Reports/{DEFAULT_CONFIG["report_id"]}?START_DATE={DEFAULT_CONFIG["start_date"]}&SUBAID={DEFAULT_CONFIG["sub_ad_id"]}',
        "@firstpageuri": f'/Advertisers/{DEFAULT_CONFIG["account_sid"]}/Reports/{DEFAULT_CONFIG["report_id"]}?PageSize=5000&Page=1&START_DATE={DEFAULT_CONFIG["start_date"]}&SUBAID={DEFAULT_CONFIG["sub_ad_id"]}',
        "@previouspageuri": "",
        "@nextpageuri": "",
        "@lastpageuri": f'/Advertisers/{DEFAULT_CONFIG["account_sid"]}/Reports/{DEFAULT_CONFIG["report_id"]}?PageSize=5000&Page=1&START_DATE={DEFAULT_CONFIG["start_date"]}&SUBAID={DEFAULT_CONFIG["sub_ad_id"]}',
        "MediaPartners": media_partners
    }
    inputs = {"response": response}

    expected_parsed_object = media_partners
    assert list(stream.parse_response(**inputs)) == expected_parsed_object


def test_report_request_headers(patch_base_class):
    stream = MediaPartners(
        authenticator=NoAuth,
        account_sid=DEFAULT_CONFIG["account_sid"],
        auth_token=DEFAULT_CONFIG["auth_token"],
        report_id=DEFAULT_CONFIG["report_id"],
        start_date=DEFAULT_CONFIG["start_date"],
        sub_ad_id=DEFAULT_CONFIG["sub_ad_id"]
    )
    inputs = {}
    expected_headers = {"Accept": "application/json", "Authorization": "Basic YWNjb3VudF9zaWQ6c29tZV90b2tlbg=="}
    assert stream.request_headers(**inputs) == expected_headers


def test_report_http_method(patch_base_class):
    stream = MediaPartners(
        authenticator=NoAuth,
        account_sid=DEFAULT_CONFIG["account_sid"],
        auth_token=DEFAULT_CONFIG["auth_token"],
        report_id=DEFAULT_CONFIG["report_id"],
        start_date=DEFAULT_CONFIG["start_date"],
        sub_ad_id=DEFAULT_CONFIG["sub_ad_id"]
    )
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_report_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = MediaPartners(
        authenticator=NoAuth,
        account_sid=DEFAULT_CONFIG["account_sid"],
        auth_token=DEFAULT_CONFIG["auth_token"],
        report_id=DEFAULT_CONFIG["report_id"],
        start_date=DEFAULT_CONFIG["start_date"],
        sub_ad_id=DEFAULT_CONFIG["sub_ad_id"]
    )
    assert stream.should_retry(response_mock) == should_retry


def test_report_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = MediaPartners(
        authenticator=NoAuth,
        account_sid=DEFAULT_CONFIG["account_sid"],
        auth_token=DEFAULT_CONFIG["auth_token"],
        report_id=DEFAULT_CONFIG["report_id"],
        start_date=DEFAULT_CONFIG["start_date"],
        sub_ad_id=DEFAULT_CONFIG["sub_ad_id"]
    )
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
