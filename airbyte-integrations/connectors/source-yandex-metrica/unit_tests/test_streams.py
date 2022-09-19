#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_yandex_metrica.streams import Check, Create, Download, Sessions, Views, YandexMetricaStream


class MockResponse(object):
    def __init__(self, json_data, status_code, **kwargs):
        self.json_data = json_data
        self.status_code = status_code
        self.__dict__.update(kwargs)

    def json(self):
        return self.json_data


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(YandexMetricaStream, "path", "v0/example_endpoint")
    mocker.patch.object(YandexMetricaStream, "primary_key", "test_primary_key")
    mocker.patch.object(YandexMetricaStream, "__abstractmethods__", set())

    kwargs = {"authenticator": TokenAuthenticator("MockOAuth2Token")}
    return {
        "views_stream": Views(
            counter_id=00000000,
            params={"start_date": "2022-07-01", "end_date": "2022-07-02", "fields": ["ym:pv:watchID", "ym:pv:dateTime"]},
            **kwargs,
        ),
        "sessions_stream": Sessions(
            counter_id=00000000,
            params={"start_date": "2022-07-01", "end_date": "2022-07-02", "fields": ["ym:s:visitID", "ym:s:dateTime"]},
            **kwargs,
        ),
        "yandex_metrica_stream": YandexMetricaStream(
            counter_id=00000000,
            params={"start_date": "2022-07-01", "end_date": "2022-07-02", "source": "hits", "fields": "ym:pv:watchID,ym:pv:dateTime"},
            **kwargs,
        ),
        "create_substream": Create(
            counter_id=00000000,
            params={"start_date": "2022-07-01", "end_date": "2022-07-02", "source": "hits", "fields": "ym:pv:watchID,ym:pv:dateTime"},
            **kwargs,
        ),
        "check_substream": Check(
            counter_id=00000000,
            params={"start_date": "2022-07-01", "end_date": "2022-07-02", "source": "hits", "fields": "ym:pv:watchID,ym:pv:dateTime"},
            logrequest_id=00000000,
            **kwargs,
        ),
        "download_substream_1_page": Download(
            counter_id=00000000,
            params={"start_date": "2022-07-01", "end_date": "2022-07-02", "source": "hits", "fields": "ym:pv:watchID,ym:pv:dateTime"},
            logrequest_id=00000000,
            last_page=0,
            **kwargs,
        ),
        "download_substream_2_pages": Download(
            counter_id=00000000,
            params={"start_date": "2022-07-01", "end_date": "2022-07-02", "source": "hits", "fields": "ym:pv:watchID,ym:pv:dateTime"},
            logrequest_id=00000000,
            last_page=1,
            **kwargs,
        ),
    }


# YandexMetrica stream tests
def test_request_headers(patch_base_class):
    stream = patch_base_class["yandex_metrica_stream"]
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}

    expected_headers = {"Content-Type": "application/x-ymetrika+json"}
    assert stream.request_headers(**inputs) == expected_headers


def test_base_url(patch_base_class):
    stream = patch_base_class["yandex_metrica_stream"]

    expected_url = "https://api-metrica.yandex.net/management/v1/counter/"
    assert stream.url_base == expected_url


def test_next_page_token(patch_base_class):
    stream = patch_base_class["yandex_metrica_stream"]

    inputs = {"response": MagicMock()}
    expected_token = None

    assert stream.next_page_token(**inputs) == expected_token


# Views stream tests
def test_views_request_params(patch_base_class):
    stream = patch_base_class["views_stream"]

    expected_params = {"date1": "2022-07-01", "date2": "2022-07-02", "source": "hits", "fields": "ym:pv:watchID,ym:pv:dateTime"}
    inputs = {"stream_slice": None, "stream_state": {}, "next_page_token": None}

    assert stream.request_params(**inputs) == expected_params


def test_views_next_page_token(patch_base_class):
    stream = patch_base_class["views_stream"]

    inputs = {"response": MagicMock()}
    expected_token = None

    assert stream.next_page_token(**inputs) == expected_token


def test_views_http_method(patch_base_class):
    stream = patch_base_class["views_stream"]

    expected_method = "GET"
    assert stream.http_method == expected_method


def test_views_path(patch_base_class):
    stream = patch_base_class["views_stream"]
    expected_path = f"{stream.counter_id}/logrequests/evaluate"

    assert stream.path() == expected_path


def test_views_schema(patch_base_class):
    stream = patch_base_class["views_stream"]
    expected_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "watchID": {"type": "string"},
            "dateTime": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"},
        },
    }

    assert stream.get_json_schema() == expected_schema


# Sessions stream tests
def test_sessions_request_params(patch_base_class):
    stream = patch_base_class["sessions_stream"]

    expected_params = {"date1": "2022-07-01", "date2": "2022-07-02", "source": "visits", "fields": "ym:s:visitID,ym:s:dateTime"}
    inputs = {"stream_slice": None, "stream_state": {}, "next_page_token": None}

    assert stream.request_params(**inputs) == expected_params


def test_sessions_next_page_token(patch_base_class):
    stream = patch_base_class["sessions_stream"]

    inputs = {"response": MagicMock()}
    expected_token = None

    assert stream.next_page_token(**inputs) == expected_token


def test_sessions_http_method(patch_base_class):
    stream = patch_base_class["sessions_stream"]

    expected_method = "GET"
    assert stream.http_method == expected_method


def test_sessions_path(patch_base_class):
    stream = patch_base_class["sessions_stream"]
    expected_path = f"{stream.counter_id}/logrequests/evaluate"

    assert stream.path() == expected_path


def test_sessions_schema(patch_base_class):
    stream = patch_base_class["sessions_stream"]
    expected_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "visitID": {"type": "string"},
            "dateTime": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"},
        },
    }

    assert stream.get_json_schema() == expected_schema


# Create substream tests
def test_create_request_params(patch_base_class):
    stream = patch_base_class["create_substream"]

    expected_params = {"date1": "2022-07-01", "date2": "2022-07-02", "source": "hits", "fields": "ym:pv:watchID,ym:pv:dateTime"}
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}

    assert stream.request_params(**inputs) == expected_params


def test_create_next_page_token(patch_base_class):
    stream = patch_base_class["create_substream"]

    inputs = {"response": MagicMock()}
    expected_token = None

    assert stream.next_page_token(**inputs) == expected_token


def test_create_http_method(patch_base_class):
    stream = patch_base_class["create_substream"]

    expected_method = "POST"
    assert stream.http_method == expected_method


def test_create_path(patch_base_class):
    stream = patch_base_class["create_substream"]
    expected_path = f"{stream.counter_id}/logrequests"

    assert stream.path() == expected_path


# Check substream tests
def test_check_request_params(patch_base_class):
    stream = patch_base_class["check_substream"]

    expected_params = {}
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}

    assert stream.request_params(**inputs) == expected_params


def test_check_next_page_token(patch_base_class):
    stream = patch_base_class["check_substream"]

    inputs = {"response": MagicMock()}
    expected_token = None

    assert stream.next_page_token(**inputs) == expected_token


def test_check_http_method(patch_base_class):
    stream = patch_base_class["check_substream"]

    expected_method = "GET"
    assert stream.http_method == expected_method


def test_check_should_retry(patch_base_class):
    stream = patch_base_class["check_substream"]
    inputs = {"response": MockResponse({"log_request": {"status": "created"}}, 200)}

    assert stream.should_retry(**inputs) is True


def test_check_should_not_retry(patch_base_class):
    stream = patch_base_class["check_substream"]
    inputs = {"response": MockResponse({"log_request": {"status": "processed"}}, 200)}

    assert stream.should_retry(**inputs) is not True


def test_check_backoff_time(patch_base_class):
    stream = patch_base_class["check_substream"]
    expected_backoff_time = 30
    inputs = {"response": MagicMock()}

    assert stream.backoff_time(**inputs) == expected_backoff_time


def test_check_max_retries(patch_base_class):
    stream = patch_base_class["check_substream"]
    expected_max_returns = 240

    assert stream.max_retries == expected_max_returns


def test_check_path(patch_base_class):
    stream = patch_base_class["check_substream"]
    expected_path = f"{stream.counter_id}/logrequest/{stream.logrequest_id}"

    assert stream.path() == expected_path


# Download substream tests
def test_download_request_params(patch_base_class):
    stream = patch_base_class["download_substream_1_page"]
    expected_params = {}
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}

    assert stream.request_params(**inputs) == expected_params


def test_download_no_next_page_token(patch_base_class):
    stream = patch_base_class["download_substream_1_page"]
    inputs = {"response": MagicMock()}
    expected_token = None

    assert stream.next_page_token(**inputs) == expected_token


def test_download_next_page_token(patch_base_class):
    stream = patch_base_class["download_substream_2_pages"]
    inputs = {"response": MagicMock(url=".../part/0/download")}
    expected_token = {"page_number": 1}

    assert stream.next_page_token(**inputs) == expected_token


def test_download_path(patch_base_class):
    stream = patch_base_class["download_substream_1_page"]
    expected_path = f"{stream.counter_id}/logrequest/{stream.logrequest_id}/part/0/download"

    assert stream.path() == expected_path


def test_download_http_method(patch_base_class):
    stream = patch_base_class["download_substream_1_page"]

    expected_method = "GET"
    assert stream.http_method == expected_method


def test_download_parse_response(patch_base_class):
    stream = patch_base_class["download_substream_1_page"]
    expected_records = [
        {"watchID": "00000000", "dateTime": "2022-07-01T12:00:00"},
        {"watchID": "00000001", "dateTime": "2022-07-01T12:00:10"},
    ]
    mock_response = MockResponse({}, 200, text="watchID\tdateTime\n00000000\t2022-07-01 12:00:00\n00000000\t2022-07-01 12:00:10")
    inputs = {"response": mock_response}

    generator = stream.parse_response(**inputs)

    assert next(generator) == expected_records[0]
