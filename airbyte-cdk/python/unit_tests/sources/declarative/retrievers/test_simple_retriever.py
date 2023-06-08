#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Mapping
from unittest.mock import MagicMock, patch

import airbyte_cdk.sources.declarative.requesters.error_handlers.response_status as response_status
import pytest
import requests
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, SyncMode, Type
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.exceptions import ReadException
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.partition_routers import SinglePartitionRouter
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import (
    SimpleRetriever,
    SimpleRetrieverTestReadDecorator,
    _prepared_request_to_airbyte_message,
    _response_to_airbyte_message,
)
from airbyte_cdk.sources.streams.http.http import HttpStream

primary_key = "pk"
records = [{"id": 1}, {"id": 2}]
request_response_logs = [
    AirbyteLogMessage(level=Level.INFO, message="request:{}"),
    AirbyteLogMessage(level=Level.INFO, message="response{}"),
]
config = {}


@patch.object(HttpStream, "_read_pages", return_value=iter([]))
def test_simple_retriever_full(mock_http_stream):
    requester = MagicMock()
    request_params = {"param": "value"}
    requester.get_request_params.return_value = request_params

    paginator = MagicMock()
    next_page_token = {"cursor": "cursor_value"}
    paginator.path.return_value = None
    paginator.next_page_token.return_value = next_page_token

    record_selector = MagicMock()
    record_selector.select_records.return_value = records

    stream_slicer = MagicMock()
    stream_slices = [{"date": "2022-01-01"}, {"date": "2022-01-02"}]
    stream_slicer.stream_slices.return_value = stream_slices

    response = requests.Response()

    underlying_state = {"date": "2021-01-01"}
    stream_slicer.get_stream_state.return_value = underlying_state

    requester.get_authenticator.return_value = NoAuth({})
    url_base = "https://airbyte.io"
    requester.get_url_base.return_value = url_base
    path = "/v1"
    requester.get_path.return_value = path
    http_method = HttpMethod.GET
    requester.get_method.return_value = http_method
    backoff_time = 60
    should_retry = ResponseStatus.retry(backoff_time)
    requester.interpret_response_status.return_value = should_retry
    request_body_json = {"body": "json"}
    requester.request_body_json.return_value = request_body_json

    request_body_data = {"body": "data"}
    requester.get_request_body_data.return_value = request_body_data
    request_body_json = {"body": "json"}
    requester.get_request_body_json.return_value = request_body_json
    request_kwargs = {"kwarg": "value"}
    requester.request_kwargs.return_value = request_kwargs
    cache_filename = "cache"
    requester.cache_filename = cache_filename
    use_cache = True
    requester.use_cache = use_cache

    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=stream_slicer,
        parameters={},
        config={},
    )

    assert retriever.primary_key == primary_key
    assert retriever.url_base == url_base
    assert retriever.path() == path
    assert retriever.state == underlying_state
    assert retriever.next_page_token(response) == next_page_token
    assert retriever.request_params(None, None, None) == request_params
    assert retriever.stream_slices(sync_mode=SyncMode.incremental) == stream_slices

    assert retriever._last_response is None
    assert retriever._last_records is None
    assert retriever.parse_response(response, stream_state={}) == records
    assert retriever._last_response == response
    assert retriever._last_records == records

    assert retriever.http_method == "GET"
    assert not retriever.raise_on_http_errors
    assert retriever.should_retry(requests.Response())
    assert retriever.backoff_time(requests.Response()) == backoff_time
    assert retriever.request_body_json(None, None, None) == request_body_json
    assert retriever.request_kwargs(None, None, None) == request_kwargs
    assert retriever.cache_filename == cache_filename
    assert retriever.use_cache == use_cache

    [r for r in retriever.read_records(SyncMode.full_refresh)]
    paginator.reset.assert_called()


@patch.object(HttpStream, "_read_pages", return_value=iter([*request_response_logs, *records]))
def test_simple_retriever_with_request_response_logs(mock_http_stream):
    requester = MagicMock()
    paginator = MagicMock()
    record_selector = MagicMock()
    stream_slicer = DatetimeBasedCursor(
        start_datetime="",
        end_datetime="",
        step="P1D",
        cursor_field="id",
        datetime_format="",
        cursor_granularity="P1D",
        config={},
        parameters={},
    )

    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=stream_slicer,
        parameters={},
        config={},
    )

    actual_messages = [r for r in retriever.read_records(SyncMode.full_refresh)]
    paginator.reset.assert_called()

    assert isinstance(actual_messages[0], AirbyteLogMessage)
    assert isinstance(actual_messages[1], AirbyteLogMessage)
    assert actual_messages[2] == records[0]
    assert actual_messages[3] == records[1]


@patch.object(HttpStream, "_read_pages", return_value=iter([]))
def test_simple_retriever_with_request_response_log_last_records(mock_http_stream):
    requester = MagicMock()
    paginator = MagicMock()
    record_selector = MagicMock()
    record_selector.select_records.return_value = request_response_logs
    response = requests.Response()
    stream_slicer = DatetimeBasedCursor(
        start_datetime="",
        end_datetime="",
        step="P1D",
        cursor_field="id",
        datetime_format="",
        cursor_granularity="P1D",
        config={},
        parameters={},
    )

    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=stream_slicer,
        parameters={},
        config={},
    )

    assert retriever._last_response is None
    assert retriever._last_records is None
    assert retriever.parse_response(response, stream_state={}) == request_response_logs
    assert retriever._last_response == response
    assert retriever._last_records == request_response_logs

    [r for r in retriever.read_records(SyncMode.full_refresh)]
    paginator.reset.assert_called()


@pytest.mark.parametrize(
    "test_name, requester_response, expected_should_retry, expected_backoff_time",
    [
        ("test_should_retry_fail", response_status.FAIL, False, None),
        ("test_should_retry_none_backoff", ResponseStatus.retry(None), True, None),
        ("test_should_retry_custom_backoff", ResponseStatus.retry(60), True, 60),
    ],
)
def test_should_retry(test_name, requester_response, expected_should_retry, expected_backoff_time):
    requester = MagicMock(use_cache=False)
    retriever = SimpleRetriever(
        name="stream_name", primary_key=primary_key, requester=requester, record_selector=MagicMock(), parameters={}, config={}
    )
    requester.interpret_response_status.return_value = requester_response
    assert retriever.should_retry(requests.Response()) == expected_should_retry
    if requester_response.action == ResponseAction.RETRY:
        assert retriever.backoff_time(requests.Response()) == expected_backoff_time


@pytest.mark.parametrize(
    "test_name, status_code, response_status, len_expected_records, expected_error",
    [
        (
            "test_parse_response_fails_if_should_retry_is_fail",
            404,
            response_status.FAIL,
            None,
            ReadException("Request None failed with response <Response [404]>"),
        ),
        ("test_parse_response_succeeds_if_should_retry_is_ok", 200, response_status.SUCCESS, 1, None),
        ("test_parse_response_succeeds_if_should_retry_is_ignore", 404, response_status.IGNORE, 0, None),
        (
            "test_parse_response_fails_with_custom_error_message",
            404,
            ResponseStatus(response_action=ResponseAction.FAIL, error_message="Custom error message override"),
            None,
            ReadException("Custom error message override"),
        ),
    ],
)
def test_parse_response(test_name, status_code, response_status, len_expected_records, expected_error):
    requester = MagicMock(use_cache=False)
    record_selector = MagicMock()
    record_selector.select_records.return_value = [{"id": 100}]
    retriever = SimpleRetriever(
        name="stream_name", primary_key=primary_key, requester=requester, record_selector=record_selector, parameters={}, config={}
    )
    response = requests.Response()
    response.request = requests.Request()
    response.status_code = status_code
    requester.interpret_response_status.return_value = response_status
    if len_expected_records is None:
        try:
            retriever.parse_response(response, stream_state={})
            assert False
        except ReadException as actual_exception:
            assert type(expected_error) is type(actual_exception)
    else:
        records = retriever.parse_response(response, stream_state={})
        assert len(records) == len_expected_records


def test_max_retries_given_error_handler_has_max_retries():
    requester = MagicMock()
    requester.error_handler = MagicMock()
    requester.error_handler.max_retries = 10
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        record_selector=MagicMock(),
        parameters={},
        config={}
    )
    assert retriever.max_retries == 10


def test_max_retries_given_error_handler_without_max_retries():
    requester = MagicMock()
    requester.error_handler = MagicMock(spec=[u'without_max_retries_attribute'])
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        record_selector=MagicMock(),
        parameters={},
        config={}
    )
    assert retriever.max_retries == 5


def test_max_retries_given_disable_retries():
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=MagicMock(),
        record_selector=MagicMock(),
        disable_retries=True,
        parameters={},
        config={}
    )
    assert retriever.max_retries == 0


@pytest.mark.parametrize(
    "test_name, response_action, retry_in, expected_backoff_time",
    [
        ("test_backoff_retriable_request", ResponseAction.RETRY, 10, 10),
        ("test_backoff_fail_request", ResponseAction.FAIL, 10, None),
        ("test_backoff_ignore_request", ResponseAction.IGNORE, 10, None),
        ("test_backoff_success_request", ResponseAction.IGNORE, 10, None),
    ],
)
def test_backoff_time(test_name, response_action, retry_in, expected_backoff_time):
    requester = MagicMock(use_cache=False)
    record_selector = MagicMock()
    record_selector.select_records.return_value = [{"id": 100}]
    response = requests.Response()
    retriever = SimpleRetriever(
        name="stream_name", primary_key=primary_key, requester=requester, record_selector=record_selector, parameters={}, config={}
    )
    if expected_backoff_time:
        requester.interpret_response_status.return_value = ResponseStatus(response_action, retry_in)
        actual_backoff_time = retriever.backoff_time(response)
        assert expected_backoff_time == actual_backoff_time
    else:
        try:
            retriever.backoff_time(response)
            assert False
        except ValueError:
            pass


@pytest.mark.parametrize(
    "test_name, paginator_mapping, stream_slicer_mapping, auth_mapping, expected_mapping",
    [
        ("test_only_base_headers", {}, {}, {}, {"key": "value"}),
        ("test_header_from_pagination", {"offset": 1000}, {}, {}, {"key": "value", "offset": 1000}),
        ("test_header_from_stream_slicer", {}, {"slice": "slice_value"}, {}, {"key": "value", "slice": "slice_value"}),
        ("test_duplicate_header_slicer", {}, {"key": "slice_value"}, {}, None),
        ("test_duplicate_header_slicer_paginator", {"k": "v"}, {"k": "slice_value"}, {}, None),
        ("test_duplicate_header_paginator", {"key": 1000}, {}, {}, None),
        ("test_only_base_and_auth_headers", {}, {}, {"AuthKey": "secretkey"}, {"key": "value", "AuthKey": "secretkey"}),
        ("test_header_from_pagination_and_auth", {"offset": 1000}, {}, {"AuthKey": "secretkey"}, {"key": "value", "offset": 1000, "AuthKey": "secretkey"}),
        ("test_duplicate_auth", {}, {"AuthKey": "secretkey"}, {"AuthKey": "secretkey"}, None),
    ],
)
def test_get_request_options_from_pagination(test_name, paginator_mapping, stream_slicer_mapping, auth_mapping, expected_mapping):
    # This test does not test request headers because they must be strings
    paginator = MagicMock()
    paginator.get_request_params.return_value = paginator_mapping
    paginator.get_request_body_data.return_value = paginator_mapping
    paginator.get_request_body_json.return_value = paginator_mapping

    stream_slicer = MagicMock()
    stream_slicer.get_request_params.return_value = stream_slicer_mapping
    stream_slicer.get_request_body_data.return_value = stream_slicer_mapping
    stream_slicer.get_request_body_json.return_value = stream_slicer_mapping

    authenticator = MagicMock()
    authenticator.get_request_params.return_value = auth_mapping
    authenticator.get_request_body_data.return_value = auth_mapping
    authenticator.get_request_body_json.return_value = auth_mapping

    base_mapping = {"key": "value"}
    requester = MagicMock(use_cache=False)
    requester.get_request_params.return_value = base_mapping
    requester.get_request_body_data.return_value = base_mapping
    requester.get_request_body_json.return_value = base_mapping
    requester.get_authenticator.return_value = authenticator

    record_selector = MagicMock()
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        record_selector=record_selector,
        paginator=paginator,
        stream_slicer=stream_slicer,
        parameters={},
        config={},
    )

    request_option_type_to_method = {
        RequestOptionType.request_parameter: retriever.request_params,
        RequestOptionType.body_data: retriever.request_body_data,
        RequestOptionType.body_json: retriever.request_body_json,
    }

    for _, method in request_option_type_to_method.items():
        if expected_mapping:
            actual_mapping = method(None, None, None)
            assert expected_mapping == actual_mapping
        else:
            try:
                method(None, None, None)
                assert False
            except ValueError:
                pass


@pytest.mark.parametrize(
    "test_name, paginator_mapping, expected_mapping",
    [
        ("test_only_base_headers", {}, {"key": "value"}),
        ("test_header_from_pagination", {"offset": 1000}, {"key": "value", "offset": "1000"}),
        ("test_duplicate_header", {"key": 1000}, None),
    ],
)
def test_get_request_headers(test_name, paginator_mapping, expected_mapping):
    # This test is separate from the other request options because request headers must be strings
    paginator = MagicMock()
    paginator.get_request_headers.return_value = paginator_mapping
    requester = MagicMock(use_cache=False)

    base_mapping = {"key": "value"}
    requester.get_request_headers.return_value = base_mapping

    record_selector = MagicMock()
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        record_selector=record_selector,
        paginator=paginator,
        parameters={},
        config={},
    )

    request_option_type_to_method = {
        RequestOptionType.header: retriever.request_headers,
    }

    for _, method in request_option_type_to_method.items():
        if expected_mapping:
            actual_mapping = method(None, None, None)
            assert expected_mapping == actual_mapping
        else:
            try:
                method(None, None, None)
                assert False
            except ValueError:
                pass


@pytest.mark.parametrize(
    "test_name, requester_body_data, paginator_body_data, expected_body_data",
    [
        ("test_only_requester_mapping", {"key": "value"}, {}, {"key": "value"}),
        ("test_only_requester_string", "key=value", {}, "key=value"),
        ("test_requester_mapping_and_paginator_no_duplicate", {"key": "value"}, {"offset": 1000}, {"key": "value", "offset": 1000}),
        ("test_requester_mapping_and_paginator_with_duplicate", {"key": "value"}, {"key": 1000}, None),
        ("test_requester_string_and_paginator", "key=value", {"offset": 1000}, None),
    ],
)
def test_request_body_data(test_name, requester_body_data, paginator_body_data, expected_body_data):
    paginator = MagicMock()
    paginator.get_request_body_data.return_value = paginator_body_data
    requester = MagicMock(use_cache=False)

    requester.get_request_body_data.return_value = requester_body_data

    record_selector = MagicMock()
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        record_selector=record_selector,
        paginator=paginator,
        parameters={},
        config={},
    )

    if expected_body_data:
        actual_body_data = retriever.request_body_data(None, None, None)
        assert expected_body_data == actual_body_data
    else:
        try:
            retriever.request_body_data(None, None, None)
            assert False
        except ValueError:
            pass


@pytest.mark.parametrize(
    "test_name, requester_path, paginator_path, expected_path",
    [
        ("test_path_from_requester", "/v1/path", None, "/v1/path"),
        ("test_path_from_paginator", "/v1/path/", "/v2/paginator", "/v2/paginator"),
    ],
)
def test_path(test_name, requester_path, paginator_path, expected_path):
    paginator = MagicMock()
    paginator.path.return_value = paginator_path
    requester = MagicMock(use_cache=False)

    requester.get_path.return_value = requester_path

    record_selector = MagicMock()
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        record_selector=record_selector,
        paginator=paginator,
        parameters={},
        config={},
    )

    actual_path = retriever.path(stream_state=None, stream_slice=None, next_page_token=None)
    assert expected_path == actual_path


@pytest.mark.parametrize(
    "test_name, http_method, url, headers, params, body_json, body_data, expected_airbyte_message",
    [
        (
            "test_basic_get_request",
            HttpMethod.GET,
            "https://airbyte.io",
            {},
            {},
            {},
            {},
            AirbyteMessage(
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO, message='request:{"url": "https://airbyte.io/", "http_method": "GET", "headers": {}, "body": null}'
                ),
            ),
        ),
        (
            "test_get_request_with_headers",
            HttpMethod.GET,
            "https://airbyte.io",
            {"h1": "v1", "h2": "v2"},
            {},
            {},
            {},
            AirbyteMessage(
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message='request:{"url": "https://airbyte.io/", "http_method": "GET", "headers": {"h1": "v1", "h2": "v2"}, "body": null}',
                ),
            ),
        ),
        (
            "test_get_request_with_request_params",
            HttpMethod.GET,
            "https://airbyte.io",
            {},
            {"p1": "v1", "p2": "v2"},
            {},
            {},
            AirbyteMessage(
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message='request:{"url": "https://airbyte.io/?p1=v1&p2=v2", "http_method": "GET", "headers": {}, "body": null}',
                ),
            ),
        ),
        (
            "test_get_request_with_request_body_json",
            HttpMethod.GET,
            "https://airbyte.io",
            {"Content-Type": "application/json"},
            {},
            {"b1": "v1", "b2": "v2"},
            {},
            AirbyteMessage(
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message='request:{"url": "https://airbyte.io/", "http_method": "GET", "headers": {"Content-Type": "application/json", "Content-Length": "24"}, "body": {"b1": "v1", "b2": "v2"}}',
                ),
            ),
        ),
        (
            "test_get_request_with_headers_params_and_body",
            HttpMethod.GET,
            "https://airbyte.io",
            {"Content-Type": "application/json", "h1": "v1"},
            {"p1": "v1", "p2": "v2"},
            {"b1": "v1", "b2": "v2"},
            {},
            AirbyteMessage(
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message='request:{"url": "https://airbyte.io/?p1=v1&p2=v2", "http_method": "GET", "headers": {"Content-Type": "application/json", "h1": "v1", "Content-Length": "24"}, "body": {"b1": "v1", "b2": "v2"}}',
                ),
            ),
        ),
        (
            "test_get_request_with_request_body_data",
            HttpMethod.GET,
            "https://airbyte.io",
            {"Content-Type": "application/json"},
            {},
            {},
            {"b1": "v1", "b2": "v2"},
            AirbyteMessage(
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message='request:{"url": "https://airbyte.io/", "http_method": "GET", "headers": {"Content-Type": "application/json", "Content-Length": "11"}, "body": {"b1": "v1", "b2": "v2"}}',
                ),
            ),
        ),
        (
            "test_basic_post_request",
            HttpMethod.POST,
            "https://airbyte.io",
            {},
            {},
            {},
            {},
            AirbyteMessage(
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message='request:{"url": "https://airbyte.io/", "http_method": "POST", "headers": {"Content-Length": "0"}, "body": null}',
                ),
            ),
        ),
    ],
)
def test_prepared_request_to_airbyte_message(test_name, http_method, url, headers, params, body_json, body_data, expected_airbyte_message):
    request = requests.Request(method=http_method.name, url=url, headers=headers, params=params)
    if body_json:
        request.json = body_json
    if body_data:
        request.data = body_data
    prepared_request = request.prepare()

    actual_airbyte_message = _prepared_request_to_airbyte_message(prepared_request)

    assert expected_airbyte_message == actual_airbyte_message


@pytest.mark.parametrize(
    "test_name, response_body, response_headers, status_code, expected_airbyte_message",
    [
        (
            "test_response_no_body_no_headers",
            b"",
            {},
            200,
            AirbyteMessage(
                type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message='response:{"body": "", "headers": {}, "status_code": 200}')
            ),
        ),
        (
            "test_response_no_body_with_headers",
            b"",
            {"h1": "v1", "h2": "v2"},
            200,
            AirbyteMessage(
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO, message='response:{"body": "", "headers": {"h1": "v1", "h2": "v2"}, "status_code": 200}'
                ),
            ),
        ),
        (
            "test_response_with_body_no_headers",
            b'{"b1": "v1", "b2": "v2"}',
            {},
            200,
            AirbyteMessage(
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message='response:{"body": "{\\"b1\\": \\"v1\\", \\"b2\\": \\"v2\\"}", "headers": {}, "status_code": 200}',
                ),
            ),
        ),
        (
            "test_response_with_body_and_headers",
            b'{"b1": "v1", "b2": "v2"}',
            {"h1": "v1", "h2": "v2"},
            200,
            AirbyteMessage(
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.INFO,
                    message='response:{"body": "{\\"b1\\": \\"v1\\", \\"b2\\": \\"v2\\"}", "headers": {"h1": "v1", "h2": "v2"}, "status_code": 200}',
                ),
            ),
        ),
    ],
)
def test_response_to_airbyte_message(test_name, response_body, response_headers, status_code, expected_airbyte_message):
    response = requests.Response()
    response.status_code = status_code
    response.headers = response_headers
    response._content = response_body

    actual_airbyte_message = _response_to_airbyte_message(response)

    assert expected_airbyte_message == actual_airbyte_message


def test_limit_stream_slices():
    maximum_number_of_slices = 4
    stream_slicer = MagicMock()
    stream_slicer.stream_slices.return_value = _generate_slices(maximum_number_of_slices * 2)
    retriever = SimpleRetrieverTestReadDecorator(
        name="stream_name",
        primary_key=primary_key,
        requester=MagicMock(),
        paginator=MagicMock(),
        record_selector=MagicMock(),
        stream_slicer=stream_slicer,
        maximum_number_of_slices=maximum_number_of_slices,
        parameters={},
        config={},
    )

    truncated_slices = list(retriever.stream_slices(sync_mode=SyncMode.incremental, stream_state=None))

    assert truncated_slices == _generate_slices(maximum_number_of_slices)


@pytest.mark.parametrize(
    "test_name, last_records, records, expected_stream_slicer_update_count",
    [
        ("test_two_records", [{"id": -1}], records, 2),
        ("test_no_records", [{"id": -1}], [], 1),
        ("test_no_records_no_previous_records", [], [], 0)
    ]
)
def test_read_records_updates_stream_slicer_once_if_no_records(test_name, last_records, records, expected_stream_slicer_update_count):
    with patch.object(HttpStream, "_read_pages", return_value=iter(records)):
        requester = MagicMock()
        paginator = MagicMock()
        record_selector = MagicMock()
        stream_slicer = MagicMock()

        retriever = SimpleRetriever(
            name="stream_name",
            primary_key=primary_key,
            requester=requester,
            paginator=paginator,
            record_selector=record_selector,
            stream_slicer=stream_slicer,
            parameters={},
            config={},
        )
        retriever._last_records = last_records

        list(retriever.read_records(sync_mode=SyncMode.incremental, stream_slice={"repository": "airbyte"}))

        assert stream_slicer.update_cursor.call_count == expected_stream_slicer_update_count


def _generate_slices(number_of_slices):
    return [{"date": f"2022-01-0{day + 1}"} for day in range(number_of_slices)]


def test_emit_log_request_response_messages():
    record_selector = MagicMock()
    record_selector.select_records.return_value = records

    request = requests.PreparedRequest()
    request.headers = {"header": "value"}
    request.url = "http://byrde.enterprises.com/casinos"

    response = requests.Response()
    response.request = request
    response.status_code = 200

    retriever = SimpleRetrieverTestReadDecorator(
        name="stream_name",
        primary_key=primary_key,
        requester=MagicMock(),
        paginator=MagicMock(),
        record_selector=record_selector,
        stream_slicer=SinglePartitionRouter(parameters={}),
        parameters={},
        config={},
    )

    request_log_message, response_log_message, record_1, record_2 = [
        record for record in retriever.parse_records(request=request, response=response, stream_slice={}, stream_state={})
    ]

    assert isinstance(request_log_message, AirbyteMessage)
    assert request_log_message.type == Type.LOG
    assert "request:" in request_log_message.log.message
    assert isinstance(response_log_message, AirbyteMessage)
    assert response_log_message.type == Type.LOG
    assert "response:" in response_log_message.log.message
    assert isinstance(record_1, Mapping)
    assert record_1 == records[0]
    assert isinstance(record_1, Mapping)
    assert record_2 == records[1]
