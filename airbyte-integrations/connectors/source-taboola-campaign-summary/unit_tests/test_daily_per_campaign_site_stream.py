#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import date, timedelta
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_taboola_campaign_summary.source import DailyPerCampaignSite


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(DailyPerCampaignSite, "path", "v0/example_endpoint")
    mocker.patch.object(DailyPerCampaignSite, "primary_key", "test_primary_key")
    mocker.patch.object(DailyPerCampaignSite, "__abstractmethods__", set())


def test_campaign_request_params(patch_base_class):
    stream = DailyPerCampaignSite(account_id="account_id")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {
        "start_date": (date.today() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "end_date": (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    }
    assert stream.request_params(**inputs) == expected_params


def test_campaign_next_page_token(patch_base_class):
    stream = DailyPerCampaignSite(account_id="account_id")
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_campaign_parse_response(patch_base_class):
    stream = DailyPerCampaignSite(account_id="account_id")
    records = [
        {"key": "value"},
        {"key": "value2"},
    ]
    response = MagicMock()
    response.json.return_value = {
        "results": records
    }
    inputs = {"response": response}

    expected_parsed_object = records
    assert list(stream.parse_response(**inputs)) == expected_parsed_object


def test_campaign_request_headers(patch_base_class):
    stream = DailyPerCampaignSite(account_id="account_id")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_campaign_http_method(patch_base_class):
    stream = DailyPerCampaignSite(account_id="account_id")
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
def test_campaign_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = DailyPerCampaignSite(account_id="account_id")
    assert stream.should_retry(response_mock) == should_retry


def test_campaign_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = DailyPerCampaignSite(account_id="account_id")
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
