#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
import datetime
import json
import random
from http import HTTPStatus
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

from source_google_analytics_data_api.source import GoogleAnalyticsDataApiGenericStream, GoogleAnalyticsDataApiTestConnectionStream

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

json_metadata_response = """
{
  "dimensions": [
    {
      "apiName": "browser",
      "uiName": "Browser",
      "description": "The browsers used to view your website.",
      "category": "Platform / Device"
    },
    {
      "apiName": "city",
      "uiName": "City",
      "description": "The city from which the user activity originated.",
      "category": "Geography"
    },
    {
      "apiName": "country",
      "uiName": "Country",
      "description": "The country from which the user activity originated.",
      "category": "Geography"
    },
    {
      "apiName": "date",
      "uiName": "Date",
      "description": "The date of the event, formatted as YYYYMMDD.",
      "category": "Time"
    },
    {
      "apiName": "deviceCategory",
      "uiName": "Device category",
      "description": "The type of device: Desktop, Tablet, or Mobile.",
      "category": "Platform / Device"
    },
    {
      "apiName": "hostName",
      "uiName": "Hostname",
      "description": "Includes the subdomain and domain names of a URL; for example, the Host Name of www.example.com/contact.html is www.example.com.",
      "category": "Page / Screen"
    },
    {
      "apiName": "operatingSystem",
      "uiName": "Operating system",
      "description": "The operating systems used by visitors to your app or website. Includes desktop and mobile operating systems such as Windows and Android.",
      "category": "Platform / Device"
    },
    {
      "apiName": "pagePathPlusQueryString",
      "uiName": "Page path + query string",
      "description": "The portion of the URL following the hostname for web pages visited; for example, the pagePathPlusQueryString portion of https://www.example.com/store/contact-us?query_string=true is /store/contact-us?query_string=true.",
      "category": "Page / Screen"
    },
    {
      "apiName": "region",
      "uiName": "Region",
      "description": "The geographic region from which the user activity originated, derived from their IP address.",
      "category": "Geography"
    },
    {
      "apiName": "sessionMedium",
      "uiName": "Session medium",
      "description": "The medium that initiated a session on your website or app.",
      "category": "Traffic Source"
    },
    {
      "apiName": "sessionSource",
      "uiName": "Session source",
      "description": "The source that initiated a session on your website or app.",
      "category": "Traffic Source"
    }
  ],
  "metrics": [
    {
      "apiName": "active1DayUsers",
      "uiName": "1-day active users",
      "description": "The number of distinct active users on your site or app within a 1 day period. The 1 day period includes the last day in the report's date range. Note: this is the same as Active Users.",
      "type": "TYPE_INTEGER",
      "category": "User"
    },
    {
      "apiName": "active28DayUsers",
      "uiName": "28-day active users",
      "description": "The number of distinct active users on your site or app within a 28 day period. The 28 day period includes the last day in the report's date range.",
      "type": "TYPE_INTEGER",
      "category": "User"
    },
    {
      "apiName": "active7DayUsers",
      "uiName": "7-day active users",
      "description": "The number of distinct active users on your site or app within a 7 day period. The 7 day period includes the last day in the report's date range.",
      "type": "TYPE_INTEGER",
      "category": "User"
    },
    {
      "apiName": "averageSessionDuration",
      "uiName": "Average session duration",
      "description": "The average duration (in seconds) of users' sessions.",
      "type": "TYPE_SECONDS",
      "category": "Session"
    },
    {
      "apiName": "bounceRate",
      "uiName": "Bounce rate",
      "description": "The percentage of sessions that were not engaged ((Sessions Minus Engaged sessions) divided by Sessions). This metric is returned as a fraction; for example, 0.2761 means 27.61% of sessions were bounces.",
      "type": "TYPE_FLOAT",
      "category": "Session"
    },
    {
      "apiName": "newUsers",
      "uiName": "New users",
      "description": "The number of users who interacted with your site or launched your app for the first time (event triggered: first_open or first_visit).",
      "type": "TYPE_INTEGER",
      "category": "User"
    },
    {
      "apiName": "screenPageViews",
      "uiName": "Views",
      "description": "The number of app screens or web pages your users viewed. Repeated views of a single page or screen are counted. (screen_view + page_view events).",
      "type": "TYPE_INTEGER",
      "category": "Page / Screen"
    },
    {
      "apiName": "screenPageViewsPerSession",
      "uiName": "Views per session",
      "description": "The number of app screens or web pages your users viewed per session. Repeated views of a single page or screen are counted. (screen_view + page_view events) / sessions.",
      "type": "TYPE_FLOAT",
      "category": "Page / Screen"
    },
    {
      "apiName": "sessions",
      "uiName": "Sessions",
      "description": "The number of sessions that began on your site or app (event triggered: session_start).",
      "type": "TYPE_INTEGER",
      "category": "Session"
    },
    {
      "apiName": "sessionsPerUser",
      "uiName": "Sessions per user",
      "description": "The average number of sessions per user (Sessions divided by Active Users).",
      "type": "TYPE_FLOAT",
      "category": "Session"
    },
    {
      "apiName": "totalUsers",
      "uiName": "Total users",
      "description": "The number of distinct users who have logged at least one event, regardless of whether the site or app was in use when that event was logged.",
      "type": "TYPE_INTEGER",
      "category": "User"
    }
  ],
  "name": "properties/496180525/metadata"
}
"""


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GoogleAnalyticsDataApiGenericStream, "path", f"{random.randint(100000000, 999999999)}:runReport")
    mocker.patch.object(GoogleAnalyticsDataApiGenericStream, "primary_key", "test_primary_key")
    mocker.patch.object(GoogleAnalyticsDataApiGenericStream, "__abstractmethods__", set())

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
            "date_ranges_start_date": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=3)), "%Y-%m-%d"),
            "window_in_days": 1
        }
    }


def test_request_params(patch_base_class):
    assert (
        GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"]).request_params(
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

    request_body_json = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"]).request_body_json(**request_body_params)
    assert request_body_json == expected_body_json


def test_next_page_token_equal_chunk(patch_base_class):
    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
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
    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
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
    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])

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

    expected_data = copy.deepcopy(response_data)
    expected_data["records"] = [
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
    actual_records: Mapping[str, Any] = next(iter(stream.parse_response(**inputs)))
    for record in actual_records["records"]:
        del record["uuid"]
    assert actual_records == expected_data


def test_metadata_retrieved_once(patch_base_class, mocker):
    read_records_mock = mocker.MagicMock()
    read_records_mock.return_value = [json.loads(json_metadata_response)]
    mocker.patch.object(GoogleAnalyticsDataApiTestConnectionStream, "read_records", read_records_mock)

    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
    metadata_one = stream.metadata
    metadata_two = stream.metadata

    assert metadata_one is metadata_two
    assert read_records_mock.call_count == 1


def test_json_schema(patch_base_class, mocker):
    read_records_mock = mocker.MagicMock()
    read_records_mock.return_value = [json.loads(json_metadata_response)]
    mocker.patch.object(GoogleAnalyticsDataApiTestConnectionStream, "read_records", read_records_mock)

    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
    json_schema_properties = stream.get_json_schema().get("properties")
    metadata = json.loads(json_metadata_response)

    metrics_metadata = {m["apiName"]: m for m in metadata["metrics"]}
    for metric in stream.config["metrics"]:
        assert metric in json_schema_properties
        assert metrics_metadata[metric]["description"] == json_schema_properties[metric]["description"]

    dimensions_metadata = {d["apiName"]: d for d in metadata["dimensions"]}
    for dimension in stream.config["dimensions"]:
        assert dimension in json_schema_properties
        assert dimensions_metadata[dimension]["description"] == json_schema_properties[dimension]["description"]

    additional_properties = ["property_id", "uuid"]
    for additional_property in additional_properties:
        assert additional_property in json_schema_properties

    assert len(stream.config["dimensions"]) + len(stream.config["metrics"]) + len(additional_properties) == len(json_schema_properties)


def test_stream_slices(patch_base_class):
    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
    stream_slices = stream.stream_slices(sync_mode=SyncMode.incremental)
    assert len(stream_slices) == 2

    latest_date = datetime.date.today()
    formatted_date_diff = lambda date, days: (date - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    assert stream_slices[0] == {"startDate": formatted_date_diff(latest_date, 3), "endDate": formatted_date_diff(latest_date, 2)}
    assert stream_slices[1] == {"startDate": formatted_date_diff(latest_date, 1), "endDate": formatted_date_diff(latest_date, 0)}


def test_read_records(patch_base_class, mocker):
    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
    initial_date = datetime.datetime.strptime(patch_base_class["config"]["date_ranges_start_date"], "%Y-%m-%d")
    formatted_date_diff = lambda date, days: (date + datetime.timedelta(days=days)).strftime("%Y%m%d")

    read_records = mocker.MagicMock()
    expected_records = [
        [
            {
                "records": [
                    {"date": formatted_date_diff(initial_date, 0)},
                    {"date": formatted_date_diff(initial_date, 1)},
                ]
            }
        ],
        [
            {
                "records": [
                    {"date": formatted_date_diff(initial_date, 2)},
                    {"date": formatted_date_diff(initial_date, 3)},
                ]
            }
        ]
    ]
    read_records.side_effect = expected_records
    mocker.patch.object(HttpStream, "read_records", read_records)

    reader = stream.read_records(
        sync_mode=SyncMode.incremental,
        stream_slice={"startDate": formatted_date_diff(initial_date, 0), "endDate": formatted_date_diff(initial_date, 1)}
    )
    assert stream._cursor_value == ""
    for i, _ in enumerate(reader):
        assert stream._cursor_value == formatted_date_diff(initial_date, i)

    reader = stream.read_records(
        sync_mode=SyncMode.incremental,
        stream_slice={"startDate": formatted_date_diff(initial_date, 2), "endDate": formatted_date_diff(initial_date, 3)}
    )
    assert stream._cursor_value == formatted_date_diff(initial_date, 1)
    for j, _ in enumerate(reader):
        assert stream._cursor_value == formatted_date_diff(initial_date, i + 1 + j)


def test_request_headers(patch_base_class):
    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
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
    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
