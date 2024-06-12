#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import random
from http import HTTPStatus
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from source_google_analytics_data_api.source import GoogleAnalyticsDataApiBaseStream, SourceGoogleAnalyticsDataApi

from .utils import read_incremental


@pytest.fixture
def patch_base_class(mocker, config, config_without_date_range):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GoogleAnalyticsDataApiBaseStream, "path", f"{random.randint(100000000, 999999999)}:runReport")
    mocker.patch.object(GoogleAnalyticsDataApiBaseStream, "primary_key", "test_primary_key")
    mocker.patch.object(GoogleAnalyticsDataApiBaseStream, "__abstractmethods__", set())

    return {"config": config, "config_without_date_range": config_without_date_range}


def test_json_schema(requests_mock, patch_base_class):
    requests_mock.register_uri(
        "POST", "https://oauth2.googleapis.com/token", json={"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer"}
    )
    requests_mock.register_uri(
        "GET",
        "https://analyticsdata.googleapis.com/v1beta/properties/108176369/metadata",
        json={
            "dimensions": [{"apiName": "date"}, {"apiName": "country"}, {"apiName": "language"}, {"apiName": "browser"}],
            "metrics": [{"apiName": "totalUsers"}, {"apiName": "screenPageViews"}, {"apiName": "sessions"}],
        },
    )
    schema = GoogleAnalyticsDataApiBaseStream(
        authenticator=MagicMock(), config={"authenticator": MagicMock(), **patch_base_class["config_without_date_range"]}
    ).get_json_schema()

    for d in patch_base_class["config_without_date_range"]["dimensions"]:
        assert d in schema["properties"]

    for p in patch_base_class["config_without_date_range"]["metrics"]:
        assert p in schema["properties"]

    assert "startDate" in schema["properties"]
    assert "endDate" in schema["properties"]


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
        "keepEmptyRows": True,
        "dateRanges": [request_body_params["stream_slice"]],
        "returnPropertyQuota": True,
        "offset": str(0),
        "limit": "100000",
    }

    request_body_json = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"]).request_body_json(
        **request_body_params
    )
    assert request_body_json == expected_body_json


def test_changed_page_size(patch_base_class):
    request_body_params = {"stream_state": MagicMock(), "stream_slice": MagicMock(), "next_page_token": None}
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"])
    stream.page_size = 100
    request_body_json = stream.request_body_json(**request_body_params)
    assert request_body_json["limit"] == "100"


def test_next_page_token_equal_chunk(patch_base_class):
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"])
    response = MagicMock()
    response.json.side_effect = [
        {"rowCount": 300000},
        {"rowCount": 300000},
        {"rowCount": 300000},
    ]
    inputs = {"response": response}

    expected_tokens = [
        {"offset": 100000},
        {"offset": 200000},
        None,
    ]

    for expected_token in expected_tokens:
        assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token(patch_base_class):
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=MagicMock(), config=patch_base_class["config"])
    response = MagicMock()
    response.json.side_effect = [
        {"rowCount": 450000},
        {"rowCount": 450000},
        {"rowCount": 450000},
        {"rowCount": 450000},
        {"rowCount": 450000},
    ]
    inputs = {"response": response}

    expected_tokens = [
        {"offset": 100000},
        {"offset": 200000},
        {"offset": 300000},
        {"offset": 400000},
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
            {"name": "sessionsPerUser:parameter", "type": "TYPE_FLOAT"},
            {"name": "averageSessionDuration", "type": "TYPE_SECONDS"},
            {"name": "screenPageViews", "type": "TYPE_INTEGER"},
            {"name": "screenPageViewsPerSession", "type": "TYPE_FLOAT"},
            {"name": "bounceRate", "type": "TYPE_FLOAT"},
        ],
        "rows": [
            {
                "dimensionValues": [{"value": "20220731"}, {"value": "desktop"}, {"value": "Macintosh"}, {"value": "Chrome"}],
                "metricValues": [
                    {"value": "344.234"},  # This is a float will be converted to int
                    {"value": "169.345345"},  # This is a float will be converted to int
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
            "property_id": "108176369",
            "date": "20220731",
            "deviceCategory": "desktop",
            "operatingSystem": "Macintosh",
            "browser": "Chrome",
            "totalUsers": 344,
            "newUsers": 169,
            "sessions": 420,
            "sessionsPerUser:parameter": 1.2209302325581395,
            "averageSessionDuration": 194.76313766428572,
            "screenPageViews": 614,
            "screenPageViewsPerSession": 1.4619047619047618,
            "bounceRate": 0.47857142857142859,
        },
        {
            "property_id": "108176369",
            "date": "20220731",
            "deviceCategory": "desktop",
            "operatingSystem": "Windows",
            "browser": "Chrome",
            "totalUsers": 322,
            "newUsers": 211,
            "sessions": 387,
            "sessionsPerUser:parameter": 1.2018633540372672,
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
        (HTTPStatus.TOO_MANY_REQUESTS, True),
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
    config = {"date_ranges_start_date": datetime.date(2022, 12, 29), "window_in_days": 1, "dimensions": ["date"]}
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=None, config=config)
    slices = list(stream.stream_slices(sync_mode=None))
    assert slices == [
        {"startDate": "2022-12-29", "endDate": "2022-12-29"},
        {"startDate": "2022-12-30", "endDate": "2022-12-30"},
        {"startDate": "2022-12-31", "endDate": "2022-12-31"},
        {"startDate": "2023-01-01", "endDate": "2023-01-01"},
    ]

    config = {"date_ranges_start_date": datetime.date(2022, 12, 28), "window_in_days": 2, "dimensions": ["date"]}
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=None, config=config)
    slices = list(stream.stream_slices(sync_mode=None))
    assert slices == [
        {"startDate": "2022-12-28", "endDate": "2022-12-29"},
        {"startDate": "2022-12-30", "endDate": "2022-12-31"},
        {"startDate": "2023-01-01", "endDate": "2023-01-01"},
    ]

    config = {"date_ranges_start_date": datetime.date(2022, 12, 20), "window_in_days": 5, "dimensions": ["date"]}
    stream = GoogleAnalyticsDataApiBaseStream(authenticator=None, config=config)
    slices = list(stream.stream_slices(sync_mode=None))
    assert slices == [
        {"startDate": "2022-12-20", "endDate": "2022-12-24"},
        {"startDate": "2022-12-25", "endDate": "2022-12-29"},
        {"startDate": "2022-12-30", "endDate": "2023-01-01"},
    ]


def test_read_incremental(requests_mock):
    config = {
        "property_ids": [123],
        "property_id": 123,
        "date_ranges_start_date": datetime.date(2022, 1, 6),
        "window_in_days": 1,
        "dimensions": ["yearWeek"],
        "metrics": ["totalUsers"],
    }

    stream = GoogleAnalyticsDataApiBaseStream(authenticator=None, config=config)
    stream_state = {}

    responses = [
        {
            "dimensionHeaders": [{"name": "yearWeek"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "202201"}], "metricValues": [{"value": "100"}]}],
            "rowCount": 1,
        },
        {
            "dimensionHeaders": [{"name": "yearWeek"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "202201"}], "metricValues": [{"value": "110"}]}],
            "rowCount": 1,
        },
        {
            "dimensionHeaders": [{"name": "yearWeek"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "202201"}], "metricValues": [{"value": "120"}]}],
            "rowCount": 1,
        },
        {
            "dimensionHeaders": [{"name": "yearWeek"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "202202"}], "metricValues": [{"value": "130"}]}],
            "rowCount": 1,
        },
        # 2-nd incremental read
        {
            "dimensionHeaders": [{"name": "yearWeek"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "202202"}], "metricValues": [{"value": "112"}]}],
            "rowCount": 1,
        },
        {
            "dimensionHeaders": [{"name": "yearWeek"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "202202"}], "metricValues": [{"value": "125"}]}],
            "rowCount": 1,
        },
        {
            "dimensionHeaders": [{"name": "yearWeek"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "202202"}], "metricValues": [{"value": "140"}]}],
            "rowCount": 1,
        },
        {
            "dimensionHeaders": [{"name": "yearWeek"}],
            "metricHeaders": [{"name": "totalUsers", "type": "TYPE_INTEGER"}],
            "rows": [{"dimensionValues": [{"value": "202202"}], "metricValues": [{"value": "150"}]}],
            "rowCount": 1,
        },
    ]

    requests_mock.register_uri(
        "POST",
        "https://analyticsdata.googleapis.com/v1beta/properties/123:runReport",
        json=lambda request, context: responses.pop(0),
    )

    with freeze_time("2022-01-09 12:00:00"):
        records = list(read_incremental(stream, stream_state))
    print(records)
    assert records == [
        {"property_id": 123, "yearWeek": "202201", "totalUsers": 100, "startDate": "2022-01-06", "endDate": "2022-01-06"},
        {"property_id": 123, "yearWeek": "202201", "totalUsers": 110, "startDate": "2022-01-07", "endDate": "2022-01-07"},
        {"property_id": 123, "yearWeek": "202201", "totalUsers": 120, "startDate": "2022-01-08", "endDate": "2022-01-08"},
        {"property_id": 123, "yearWeek": "202202", "totalUsers": 130, "startDate": "2022-01-09", "endDate": "2022-01-09"},
    ]

    assert stream_state == {"yearWeek": "202202"}

    with freeze_time("2022-01-10 12:00:00"):
        records = list(read_incremental(stream, stream_state))

    assert records == [
        {"property_id": 123, "yearWeek": "202202", "totalUsers": 112, "startDate": "2022-01-08", "endDate": "2022-01-08"},
        {"property_id": 123, "yearWeek": "202202", "totalUsers": 125, "startDate": "2022-01-09", "endDate": "2022-01-09"},
        {"property_id": 123, "yearWeek": "202202", "totalUsers": 140, "startDate": "2022-01-10", "endDate": "2022-01-10"},
    ]

@pytest.mark.parametrize(
    "config_dimensions, expected_state",
    [
        pytest.param(["browser", "country", "language", "date"], {"date": "20240320"}, id="test_date_no_cursor_field_dimension"),
        pytest.param(["browser", "country", "language"], {}, id="test_date_cursor_field_dimension"),
    ]
)
def test_get_updated_state(config_dimensions, expected_state):
    config = {
      "credentials": {
        "auth_type": "Service",
        "credentials_json": "{ \"client_email\": \"a@gmail.com\", \"client_id\": \"1234\", \"client_secret\": \"5678\", \"private_key\": \"5678\"}"
      },
      "date_ranges_start_date": "2023-04-01",
      "window_in_days": 30,
      "property_ids": ["123"],
      "custom_reports_array": [
        {
          "name": "pivot_report",
          "dateRanges": [{"startDate": "2020-09-01", "endDate": "2020-09-15"}],
          "dimensions": config_dimensions,
          "metrics": ["sessions"],
          "pivots": [
            {
              "fieldNames": ["browser"],
              "limit": 5
            },
            {
              "fieldNames": ["country"],
              "limit": 250
            },
            {
              "fieldNames": ["language"],
              "limit": 15
            }
          ],
          "cohortSpec": {
            "enabled": "false"
          }
        }
      ]
    }
    source = SourceGoogleAnalyticsDataApi()
    config = source._validate_and_transform(config, report_names=set())
    config["authenticator"] = source.get_authenticator(config)
    report_stream = source.instantiate_report_class(config["custom_reports_array"][0], False, config, page_size=100)

    actual_state = report_stream.get_updated_state(current_stream_state={}, latest_record={"date": "20240320"})

    assert actual_state == expected_state
