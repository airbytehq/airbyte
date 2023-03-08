#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import requests
from source_exact.streams import ExactOtherStream, ExactSyncStream


class MyTestExactSyncStream(ExactSyncStream):
    endpoint = "sync/mocked"

    @property
    def _auth(self):
        return MagicMock()

    def get_json_schema(self):
        return {
            "properties": {
                "ID": {"type": ["null", "string"]},
                "Timestamp": {"type": ["null", "integer"]},
                "IntField": {"type": ["null", "integer"]},
                "FloatField": {"type": ["null", "number"]},
                "BoolField": {"type": ["null", "boolean"]},
            }
        }


class MyTestExactOtherStream(ExactOtherStream):
    endpoint = "other/mocked"

    @property
    def _auth(self):
        return MagicMock()

    def get_json_schema(self):
        return {
            "properties": {
                "ID": {"type": ["null", "integer"]},
                "Modified": {"type": ["null", "string"]},
            }
        }


class MyTestRequestException(requests.RequestException):
    pass


def test_path__failure(config_oauth):
    stream = MyTestExactSyncStream(config_oauth)
    stream.endpoint = None

    with pytest.raises(RuntimeError, match="Subclass is missing endpoint"):
        stream.path(None)


def test_path__next_page(config_oauth):
    assert MyTestExactSyncStream(config_oauth).path({"next_url": "example.com/next"}) == "example.com/next"


def test_path__initial(config_oauth):
    stream = MyTestExactSyncStream(config_oauth)
    assert stream.path(None) == stream.endpoint


def test_request_headers(config_oauth: dict):
    assert MyTestExactSyncStream(config_oauth).request_headers() == {"Accept": "application/json"}


def test_request_params_with_next_page(config_oauth: dict):
    assert MyTestExactSyncStream(config_oauth).request_params(next_page_token="someting") == {}


@pytest.mark.parametrize(
    "next_page_token, cursor_value, expected",
    [
        ("token", None, {}),
        ("token", "123", {}),
        (None, None, {"$select": "ID,Timestamp,IntField,FloatField,BoolField"}),
        (None, "123", {"$filter": "Timestamp gt 123L", "$select": "ID,Timestamp,IntField,FloatField,BoolField"}),
    ],
)
def test_request_params_with_sync_stream(config_oauth: dict, next_page_token, cursor_value, expected):
    stream = MyTestExactSyncStream(config_oauth)
    stream.state = {"456": { "Timestamp": cursor_value } }

    assert stream.request_params(next_page_token, {"division": "456"}) == expected

@pytest.mark.parametrize(
    "next_page_token, cursor_value, expected",
    [
        ("token", None, {}),
        ("token", "2022-12-12T00:00:00+00:00", {}),
        (None, None, {"$orderby": "Modified asc", "$select": "ID,Modified"}),
        (None, "2022-12-12T00:00:00+00:00", {"$filter": "Modified gt datetime'2022-12-12T01:00:00'", "$orderby": "Modified asc", "$select": "ID,Modified",}),
        # Test if resilient to other types of formatting
        (None, "2022-12-12T00:00:00Z", {"$filter": "Modified gt datetime'2022-12-12T01:00:00'", "$orderby": "Modified asc", "$select": "ID,Modified"}),
        # Should not happen: input is a timestamp not in UTC! A warning is logged.
        (None, "2022-12-12T00:00:00+01:00", {"$filter": "Modified gt datetime'2022-12-12T00:00:00'", "$orderby": "Modified asc", "$select": "ID,Modified"}),
        # Test if UTC is correctly handled in summer time
        (None, "2022-06-12T00:00:00+00:00", {"$filter": "Modified gt datetime'2022-06-12T02:00:00'", "$orderby": "Modified asc", "$select": "ID,Modified"}),
    ],
)
def test_request_params_with_other_stream(config_oauth: dict, next_page_token, cursor_value, expected):
    stream = MyTestExactOtherStream(config_oauth)
    stream.state = {"456": { "Modified": cursor_value } }

    assert stream.request_params(next_page_token, {"division": "456"}) == expected

@pytest.mark.parametrize(
    "body, expected",
    [
        ({}, None),
        ({"d": {"__next": None}}, None),
        ({"d": {"__next": "example.com/next?page=123"}}, {"next_url": "example.com/next?page=123"}),
    ],
)
def test_next_page_token(config_oauth: dict, body: dict, expected: dict):
    response_mock = MagicMock()
    response_mock.json.return_value = body

    assert MyTestExactSyncStream(config_oauth).next_page_token(response_mock) == expected


@pytest.mark.parametrize(
    "body, expected",
    [
        ({}, []),
        ({"d": {}}, []),
        ({"d": {"results": [1, 2, 3]}}, [1, 2, 3]),
    ],
)
def test_parse_response(config_oauth: dict, body, expected):
    response_mock = MagicMock()
    response_mock.json.return_value = body

    assert MyTestExactSyncStream(config_oauth).parse_response(response_mock) == expected


def test_is_token_expired__not_expired(config_oauth):
    response_mock = MagicMock()
    response_mock.status_code = 200

    assert not MyTestExactSyncStream(config_oauth)._is_token_expired(response_mock)


def test_is_token_expired__expired(config_oauth):
    response_mock = MagicMock()
    response_mock.status_code = 401
    response_mock.headers = {"WWW-Authenticate": "access token expired"}

    assert MyTestExactSyncStream(config_oauth)._is_token_expired(response_mock)


def test_is_token_expired__failure(config_oauth):
    response_mock = MagicMock()
    response_mock.status_code = 401
    response_mock.headers = {"WWW-Authenticate": "can't access this resource"}

    with pytest.raises(RuntimeError, match="Unexpected forbidden error"):
        MyTestExactSyncStream(config_oauth)._is_token_expired(response_mock)


def test_parse_item__nested_timestamps(config_oauth: dict):
    # This test doesn't follow the defined JSON Schema. Instead, here we validate whether all (nested) occurrences
    # of timestamps are parsed correctly.

    obj = {
        "date": "/Date(1640995200000)/", # 2022-01-01T00:00:00+00:00 in CET wintertime (UTC +1 hours)
        "nested": {
            "date": "/Date(1640995200000)/", # 2022-01-01T00:00:00+00:00 in CET wintertime (UTC +1 hours)
        },
        "array": ["/Date(1640995200000)/"], # 2022-01-01T00:00:00+00:00 in CET wintertime (UTC +1 hours)
        "array_with_nested": [{"date": "/Date(1640995200000)/"}], # 2022-01-01T00:00:00+00:00 in CET wintertime (UTC +1 hours)
        "date_summer": "/Date(1655894855020)/", # 2022-06-22T10:47:35.02 in CET summertime (UTC +2 hours)
        "date_winter": "/Date(1669134984190)/", # 2022-11-22T16:36:24.19 in CET wintertime (UTC +1 hours)
    }
    assert MyTestExactSyncStream(config_oauth)._parse_item(obj) == {
        "date": "2021-12-31T23:00:00+00:00",
        "nested": {"date": "2021-12-31T23:00:00+00:00"},
        "array": ["2021-12-31T23:00:00+00:00"],
        "array_with_nested": [{"date": "2021-12-31T23:00:00+00:00"}],
        "date_summer": "2022-06-22T08:47:35.020000+00:00",
        "date_winter": "2022-11-22T15:36:24.190000+00:00",
    }


def test_parse_item__type_casting(config_oauth: dict):
    # This follows the defined schema and also checks whether correct type casting is done.

    obj = {
        "ID": "entity-100",
        "Timestamp": 123,
        "IntField": "456",  # explicit str as that also is how Exact can return the data
        "FloatField": "7.89",  # explicit str as that also is how Exact can return the data
        "BoolField": "true",  # explicit str as that also is how Exact can return the data
    }
    assert MyTestExactSyncStream(config_oauth)._parse_item(obj) == {
        "ID": "entity-100",
        "Timestamp": 123,
        "IntField": 456,
        "FloatField": 7.89,
        "BoolField": True,
    }


def test_send_request__reraise_if_on_non_request_exception(config_oauth):
    request_mock, request_kwargs = MagicMock(), MagicMock()

    stream = MyTestExactSyncStream(config_oauth)
    stream._send = MagicMock(side_effect=RuntimeError("Random Error"))

    with pytest.raises(RuntimeError, match="Random Error"):
        stream._send_request(request_mock, request_kwargs)


def test_send_request__reraise_if_response_missing_on_exception(config_oauth):
    request_mock, request_kwargs = MagicMock(), MagicMock()

    stream = MyTestExactSyncStream(config_oauth)
    stream._send = MagicMock(side_effect=MyTestRequestException("Missing Response"))

    with pytest.raises(MyTestRequestException, match="Missing Response"):
        stream._send_request(request_mock, request_kwargs)


def test_send_request__reraise_if_not_retryable_exception(config_oauth):
    request_mock, request_kwargs, response_mock = MagicMock(), MagicMock(), MagicMock()
    response_mock.status_code = 400

    stream = MyTestExactSyncStream(config_oauth)
    stream._send = MagicMock(side_effect=MyTestRequestException("BadRequest", response=response_mock))

    with pytest.raises(MyTestRequestException, match="BadRequest"):
        stream._send_request(request_mock, request_kwargs)


def test_send_request__retries_on_server_error(config_oauth):
    request_mock, request_kwargs, response_mock = MagicMock(), MagicMock(), MagicMock()
    response_mock.status_code = 500

    stream = MyTestExactSyncStream(config_oauth)
    stream._send = MagicMock(side_effect=MyTestRequestException("ServerError", response=response_mock))

    stream._send_request(request_mock, request_kwargs)

    assert stream.max_retries > 0
    assert stream._send.call_count == stream.max_retries


def test_send_request__retries_on_expired_token(config_oauth):
    request_mock, request_kwargs, response_mock = MagicMock(), MagicMock(), MagicMock()
    response_mock.status_code = 401
    response_mock.headers = {"WWW-Authenticate": "access token expired"}

    stream = MyTestExactSyncStream(config_oauth)
    stream._send = MagicMock(side_effect=MyTestRequestException("Forbidden", response=response_mock))
    stream._is_token_expired = MagicMock(return_value=True)
    stream._single_refresh_token_authenticator = MagicMock()

    stream._send_request(request_mock, request_kwargs)

    assert stream.max_retries > 0
    assert stream._send.call_count == stream.max_retries
