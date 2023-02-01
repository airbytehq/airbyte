#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import random
from http import HTTPStatus
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from source_google_analytics_data_api.source import GoogleAnalyticsDataApiBaseStream

from .utils import read_incremental

json_credentials = """
{
    "type": "service_account",
    "project_id": "unittest-project-id",
    "private_key_id": "9qf98e52oda52g5ne23al6evnf13649c2u077162c",
    "private_key": "",
    "client_email": "google-analytics-access@unittest-project-id.iam.gserviceaccount.com",
    "client_id": "213243192021686092537",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-analytics-access%40unittest-project-id.iam.gserviceaccount.com"
}
"""


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GoogleAnalyticsDataApiBaseStream, "path", f"{random.randint(100000000, 999999999)}:runReport")
    mocker.patch.object(GoogleAnalyticsDataApiBaseStream, "primary_key", "test_primary_key")
    mocker.patch.object(GoogleAnalyticsDataApiBaseStream, "__abstractmethods__", set())

    return {
        "config": {
            "property_id": "496180525",
            "credentials": {"auth_type": "Service", "credentials_json": json_credentials},
            "dimensions": ["date", "deviceCategory", "operatingSystem", "browser"],
            "metrics": [
                "totalUsers",
                "newUsers",
                "sessions",
                "sessionsPerUser",
                "averageSessionDuration",
                "screenPageViews",
                "screenPageViewsPerSession",
                "bounceRate",
            ],
            "date_ranges_start_date": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d"),
        }
    }


def test_request_params(patch_base_class):
    assert (
        GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"]).request_params(
            stream_state=MagicMock(), stream_slice=MagicMock(), next_page_token=MagicMock()
        )
        == {}
    )


def test_request_body_json(patch_base_class):
    request_body_params = {"stream_state": MagicMock(), "stream_slice": MagicMock(), "next_page_token": None}

    expected_body_json = {
        "metrics": [
            {"name": "totalUsers"},
            {"name": "newUsers"},
            {"name": "sessions"},
            {"name": "sessionsPerUser"},
            {"name": "averageSessionDuration"},
            {"name": "screenPageViews"},
            {"name": "screenPageViewsPerSession"},
            {"name": "bounceRate"},
        ],
        "dimensions": [
            {"name": "date"},
            {"name": "deviceCategory"},
            {"name": "operatingSystem"},
            {"name": "browser"},
        ],
        "dateRanges": [request_body_params["stream_slice"]],
    }

    request_body_json = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"]).request_body_json(**request_body_params)
    assert request_body_json == expected_body_json


def test_next_page_token_equal_chunk(patch_base_class):
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"])
    response = MagicMock()
    response.json.side_effect = [
        {"limit": 100000, "offset": 0, "rowCount": 200000},
        {"limit": 100000, "offset": 100000, "rowCount": 200000},
        {"limit": 100000, "offset": 200000, "rowCount": 200000},
    ]
    inputs = {"response": response}

    expected_tokens = [
        {
            "limit": 100000,
            "offset": 100000,
        },
        {
            "limit": 100000,
            "offset": 200000,
        },
        None,
    ]

    for expected_token in expected_tokens:
        assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token(patch_base_class):
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"])
    response = MagicMock()
    response.json.side_effect = [
        {"limit": 100000, "offset": 0, "rowCount": 250000},
        {"limit": 100000, "offset": 100000, "rowCount": 250000},
        {"limit": 100000, "offset": 200000, "rowCount": 250000},
        {"limit": 100000, "offset": 300000, "rowCount": 250000},
    ]
    inputs = {"response": response}

    expected_tokens = [
        {
            "limit": 100000,
            "offset": 100000,
        },
        {
            "limit": 100000,
            "offset": 200000,
        },
        {
            "limit": 100000,
            "offset": 300000,
        },
        None,
    ]

    for expected_token in expected_tokens:
        assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"])

    response_data = {
        "dimensionHeaders": [{"name": "date"}, {"name": "deviceCategory"}, {"name": "operatingSystem"}, {"name": "browser"}],
        "metricHeaders": [
            {"name": "totalUsers", "type": "TYPE_INTEGER"},
            {"name": "newUsers", "type": "TYPE_INTEGER"},
            {"name": "sessions", "type": "TYPE_INTEGER"},
            {"name": "sessionsPerUser", "type": "TYPE_FLOAT"},
            {"name": "averageSessionDuration", "type": "TYPE_SECONDS"},
            {"name": "screenPageViews", "type": "TYPE_INTEGER"},
            {"name": "screenPageViewsPerSession", "type": "TYPE_FLOAT"},
            {"name": "bounceRate", "type": "TYPE_FLOAT"},
        ],
        "rows": [
            {
                "dimensionValues": [{"value": "20220731"}, {"value": "desktop"}, {"value": "Macintosh"}, {"value": "Chrome"}],
                "metricValues": [
                    {"value": "344"},
                    {"value": "169"},
                    {"value": "420"},
                    {"value": "1.2209302325581395"},
                    {"value": "194.76313766428572"},
                    {"value": "614"},
                    {"value": "1.4619047619047618"},
                    {"value": "0.47857142857142859"},
                ],
            },
            {
                "dimensionValues": [{"value": "20220731"}, {"value": "desktop"}, {"value": "Windows"}, {"value": "Chrome"}],
                "metricValues": [
                    {"value": "322"},
                    {"value": "211"},
                    {"value": "387"},
                    {"value": "1.2018633540372672"},
                    {"value": "249.21595714211884"},
                    {"value": "669"},
                    {"value": "1.7286821705426356"},
                    {"value": "0.42377260981912146"},
                ],
            },
        ],
        "rowCount": 54,
        "metadata": {"currencyCode": "USD", "timeZone": "America/Los_Angeles"},
        "kind": "analyticsData#runReport",
    }

    expected_data = [
        {
            "property_id": "496180525",
            "date": "20220731",
            "deviceCategory": "desktop",
            "operatingSystem": "Macintosh",
            "browser": "Chrome",
            "totalUsers": 344,
            "newUsers": 169,
            "sessions": 420,
            "sessionsPerUser": 1.2209302325581395,
            "averageSessionDuration": 194.76313766428572,
            "screenPageViews": 614,
            "screenPageViewsPerSession": 1.4619047619047618,
            "bounceRate": 0.47857142857142859,
        },
        {
            "property_id": "496180525",
            "date": "20220731",
            "deviceCategory": "desktop",
            "operatingSystem": "Windows",
            "browser": "Chrome",
            "totalUsers": 322,
            "newUsers": 211,
            "sessions": 387,
            "sessionsPerUser": 1.2018633540372672,
            "averageSessionDuration": 249.21595714211884,
            "screenPageViews": 669,
            "screenPageViewsPerSession": 1.7286821705426356,
            "bounceRate": 0.42377260981912146,
        },
    ]

    response = MagicMock()
    response.json.return_value = response_data
    inputs = {"response": response, "stream_state": {}}
    actual_records: Mapping[str, Any] = list(stream.parse_response(**inputs))
    for record in actual_records:
        del record["uuid"]
    assert actual_records == expected_data


def test_request_headers(patch_base_class):
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"])
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"])
    expected_method = "POST"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, False),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"])
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"])
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


@freeze_time("2023-01-01 00:00:00")
def test_stream_slices():
    config = {"date_ranges_start_date": datetime.date(2022, 12, 29), "window_in_days": 1}
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=None, config=config)
    slices = list(stream.stream_slices(sync_mode=None))
    assert slices == [
        {"startDate": "2022-12-29", "endDate": "2022-12-29"},
        {"startDate": "2022-12-30", "endDate": "2022-12-30"},
        {"startDate": "2022-12-31", "endDate": "2022-12-31"},
        {"startDate": "2023-01-01", "endDate": "2023-01-01"},
    ]

    config = {"date_ranges_start_date": datetime.date(2022, 12, 28), "window_in_days": 2}
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=None, config=config)
    slices = list(stream.stream_slices(sync_mode=None))
    assert slices == [
        {"startDate": "2022-12-28", "endDate": "2022-12-29"},
        {"startDate": "2022-12-30", "endDate": "2022-12-31"},
        {"startDate": "2023-01-01", "endDate": "2023-01-01"},
    ]

    config = {"date_ranges_start_date": datetime.date(2022, 12, 20), "window_in_days": 5}
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=None, config=config)
    slices = list(stream.stream_slices(sync_mode=None))
    assert slices == [
        {"startDate": "2022-12-20", "endDate": "2022-12-24"},
        {"startDate": "2022-12-25", "endDate": "2022-12-29"},
        {"startDate": "2022-12-30", "endDate": "2023-01-01"},
    ]


def test_read_incremental(requests_mock):
    config = {
        "property_id": 123,
        "date_ranges_start_date": datetime.date(2022, 12, 29),
        "window_in_days": 1,
        "dimensions": ["date"],
        "metrics": ["totalUsers"],
    }

    stream = GoogleAnalyticsDataApiBaseStream(authenticator=None, config=config)
    stream_state = {}

    responses = [
        {
            "dimensionHeaders": [{"name": "date"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "20221229"}], "metricValues": [{"value": "100"}]}],
            "rowCount": 1
        },
        {
            "dimensionHeaders": [{"name": "date"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "20221230"}], "metricValues": [{"value": "110"}]}],
            "rowCount": 1
        },
        {
            "dimensionHeaders": [{"name": "date"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "20221231"}], "metricValues": [{"value": "120"}]}],
            "rowCount": 1
        },
        {
            "dimensionHeaders": [{"name": "date"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "20230101"}], "metricValues": [{"value": "130"}]}],
            "rowCount": 1
        },
        {
            "dimensionHeaders": [{"name": "date"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "20230101"}], "metricValues": [{"value": "140"}]}],
            "rowCount": 1
        },
        {
            "dimensionHeaders": [{"name": "date"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "20230102"}], "metricValues": [{"value": "150"}]}],
            "rowCount": 1
        }
    ]

    requests_mock.register_uri(
        "POST",
        "https://analyticsdata.googleapis.com/v1beta/properties/123:runReport",
        json=lambda request, context: responses.pop(0),
    )

    with freeze_time("2023-01-01 12:00:00"):
        records = list(read_incremental(stream, stream_state))

    for record in records:
        del record["uuid"]

    assert records == [
        {"date": "20221229", "totalUsers": 100, "property_id": 123},
        {"date": "20221230", "totalUsers": 110, "property_id": 123},
        {"date": "20221231", "totalUsers": 120, "property_id": 123},
        {"date": "20230101", "totalUsers": 130, "property_id": 123},
    ]

    assert stream_state == {"date": "20230101"}

    with freeze_time("2023-01-02 12:00:00"):
        records = list(read_incremental(stream, stream_state))

    for record in records:
        del record["uuid"]

    assert records == [
        {"date": "20230101", "totalUsers": 140, "property_id": 123},
        {"date": "20230102", "totalUsers": 150, "property_id": 123},
    ]
