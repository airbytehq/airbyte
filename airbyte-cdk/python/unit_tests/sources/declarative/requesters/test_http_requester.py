#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from typing import Any, Mapping, Optional
from unittest import mock
from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlparse

import pytest as pytest
import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator, NoAuth
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.exceptions import ReadException
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpMethod, HttpRequester
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from requests import PreparedRequest


def test_http_requester():
    http_method = "GET"

    request_options_provider = MagicMock()
    request_params = {"param": "value"}
    request_body_data = "body_key_1=value_1&body_key_2=value2"
    request_body_json = {"body_field": "body_value"}
    request_options_provider.get_request_params.return_value = request_params
    request_options_provider.get_request_body_data.return_value = request_body_data
    request_options_provider.get_request_body_json.return_value = request_body_json

    request_headers_provider = MagicMock()
    request_headers = {"header": "value"}
    request_headers_provider.get_request_headers.return_value = request_headers

    authenticator = MagicMock()

    error_handler = MagicMock()
    max_retries = 10
    backoff_time = 1000
    response_status = MagicMock()
    response_status.retry_in.return_value = 10
    error_handler.max_retries = max_retries
    error_handler.interpret_response.return_value = response_status
    error_handler.backoff_time.return_value = backoff_time

    config = {"url": "https://airbyte.io"}
    stream_slice = {"id": "1234"}

    name = "stream_name"

    requester = HttpRequester(
        name=name,
        url_base=InterpolatedString.create("{{ config['url'] }}", parameters={}),
        path=InterpolatedString.create("v1/{{ stream_slice['id'] }}", parameters={}),
        http_method=http_method,
        request_options_provider=request_options_provider,
        authenticator=authenticator,
        error_handler=error_handler,
        config=config,
        parameters={},
    )

    assert requester.get_url_base() == "https://airbyte.io/"
    assert requester.get_path(stream_state={}, stream_slice=stream_slice, next_page_token={}) == "v1/1234"
    assert requester.get_authenticator() == authenticator
    assert requester.get_method() == HttpMethod.GET
    assert requester.get_request_params(stream_state={}, stream_slice=None, next_page_token=None) == request_params
    assert requester.get_request_body_data(stream_state={}, stream_slice=None, next_page_token=None) == request_body_data
    assert requester.get_request_body_json(stream_state={}, stream_slice=None, next_page_token=None) == request_body_json
    assert requester.interpret_response_status(requests.Response()) == response_status
    assert {} == requester.request_kwargs(stream_state={}, stream_slice=None, next_page_token=None)


@pytest.mark.parametrize(
    "test_name, base_url, expected_base_url",
    [
        ("test_no_trailing_slash", "https://example.com", "https://example.com/"),
        ("test_with_trailing_slash", "https://example.com/", "https://example.com/"),
        ("test_with_v1_no_trailing_slash", "https://example.com/v1", "https://example.com/v1/"),
        ("test_with_v1_with_trailing_slash", "https://example.com/v1/", "https://example.com/v1/"),
    ],
)
def test_base_url_has_a_trailing_slash(test_name, base_url, expected_base_url):
    requester = HttpRequester(
        name="name",
        url_base=base_url,
        path="deals",
        http_method=HttpMethod.GET,
        request_options_provider=MagicMock(),
        authenticator=MagicMock(),
        error_handler=MagicMock(),
        config={},
        parameters={},
    )
    assert requester.get_url_base() == expected_base_url


@pytest.mark.parametrize(
    "test_name, path, expected_path",
    [
        ("test_no_leading_slash", "deals", "deals"),
        ("test_with_leading_slash", "/deals", "deals"),
        ("test_with_v1_no_leading_slash", "v1/deals", "v1/deals"),
        ("test_with_v1_with_leading_slash", "/v1/deals", "v1/deals"),
        ("test_with_v1_with_trailing_slash", "v1/deals/", "v1/deals/"),
    ],
)
def test_path(test_name, path, expected_path):
    requester = HttpRequester(
        name="name",
        url_base="https://example.com",
        path=path,
        http_method=HttpMethod.GET,
        request_options_provider=MagicMock(),
        authenticator=MagicMock(),
        error_handler=MagicMock(),
        config={},
        parameters={},
    )
    assert requester.get_path(stream_state={}, stream_slice={}, next_page_token={}) == expected_path


def create_requester(url_base: Optional[str] = None, parameters: Optional[Mapping[str, Any]] = {}, config: Optional[Config] = None, path: Optional[str] = None, authenticator: Optional[DeclarativeAuthenticator] = None, error_handler: Optional[ErrorHandler] = None) -> HttpRequester:
    requester = HttpRequester(
        name="name",
        url_base=url_base or "https://example.com",
        path=path or "deals",
        http_method=HttpMethod.GET,
        request_options_provider=None,
        authenticator=authenticator,
        error_handler=error_handler,
        config=config or {},
        parameters=parameters or {},
    )
    requester._session.send = MagicMock()
    req = requests.Response()
    req.status_code = 200
    requester._session.send.return_value = req
    return requester


def test_basic_send_request():
    options_provider = MagicMock()
    options_provider.get_request_headers.return_value = {"my_header": "my_value"}
    requester = create_requester()
    requester._request_options_provider = options_provider
    requester.send_request()
    sent_request: PreparedRequest = requester._session.send.call_args_list[0][0][0]
    assert sent_request.method == "GET"
    assert sent_request.url == "https://example.com/deals"
    assert sent_request.headers["my_header"] == "my_value"
    assert sent_request.body is None


@pytest.mark.parametrize(
    "provider_data, provider_json, param_data, param_json, authenticator_data, authenticator_json, expected_exception, expected_body",
    [
        # merging data params from the three sources
        ({"field": "value"}, None, None, None, None, None, None, "field=value"),
        ({"field": "value"}, None, {"field2": "value"}, None, None, None, None, "field=value&field2=value"),
        ({"field": "value"}, None, {"field2": "value"}, None, {"authfield": "val"}, None, None, "field=value&field2=value&authfield=val"),
        ({"field": "value"}, None, {"field": "value"}, None, None, None, ValueError, None),
        ({"field": "value"}, None, None, None, {"field": "value"}, None, ValueError, None),
        ({"field": "value"}, None, {"field2": "value"}, None, {"field": "value"}, None, ValueError, None),
        # merging json params from the three sources
        (None, {"field": "value"}, None, None, None, None, None, '{"field": "value"}'),
        (None, {"field": "value"}, None, {"field2": "value"}, None, None, None, '{"field": "value", "field2": "value"}'),
        (None, {"field": "value"}, None, {"field2": "value"}, None, {"authfield": "val"}, None, '{"field": "value", "field2": "value", "authfield": "val"}'),
        (None, {"field": "value"}, None, {"field": "value"}, None, None, ValueError, None),
        (None, {"field": "value"}, None, None, None, {"field": "value"}, ValueError, None),
        # raise on mixed data and json params
        ({"field": "value"}, {"field": "value"}, None, None, None, None, RequestBodyException, None),
        ({"field": "value"}, None, None, {"field": "value"}, None, None, RequestBodyException, None),
        (None, None, {"field": "value"}, {"field": "value"}, None, None, RequestBodyException, None),
        (None, None, None, None, {"field": "value"}, {"field": "value"}, RequestBodyException, None),
        ({"field": "value"}, None, None, None, None, {"field": "value"}, RequestBodyException, None),

    ])
def test_send_request_data_json(provider_data, provider_json, param_data, param_json, authenticator_data, authenticator_json, expected_exception, expected_body):
    options_provider = MagicMock()
    options_provider.get_request_body_data.return_value = provider_data
    options_provider.get_request_body_json.return_value = provider_json
    authenticator = MagicMock()
    authenticator.get_request_body_data.return_value = authenticator_data
    authenticator.get_request_body_json.return_value = authenticator_json
    requester = create_requester(authenticator=authenticator)
    requester._request_options_provider = options_provider
    if expected_exception is not None:
        with pytest.raises(expected_exception):
            requester.send_request(request_body_data=param_data, request_body_json=param_json)
    else:
        requester.send_request(request_body_data=param_data, request_body_json=param_json)
        sent_request: PreparedRequest = requester._session.send.call_args_list[0][0][0]
        if expected_body is not None:
            assert sent_request.body == expected_body.decode('UTF-8') if not isinstance(expected_body, str) else expected_body


@pytest.mark.parametrize(
    "provider_data, param_data, authenticator_data, expected_exception, expected_body",
    [
        # assert body string from one source works
        ("field=value", None, None, None, "field=value"),
        (None, "field=value", None, None, "field=value"),
        (None, None, "field=value", None, "field=value"),
        # assert body string from multiple sources fails
        ("field=value", "field=value", None, ValueError, None),
        ("field=value", None, "field=value", ValueError, None),
        (None, "field=value", "field=value", ValueError, None),
        ("field=value", "field=value", "field=value", ValueError, None),
    ]
)
def test_send_request_string_data(provider_data, param_data, authenticator_data, expected_exception, expected_body):
    options_provider = MagicMock()
    options_provider.get_request_body_data.return_value = provider_data
    authenticator = MagicMock()
    authenticator.get_request_body_data.return_value = authenticator_data
    requester = create_requester(authenticator=authenticator)
    requester._request_options_provider = options_provider
    if expected_exception is not None:
        with pytest.raises(expected_exception):
            requester.send_request(request_body_data=param_data)
    else:
        requester.send_request(request_body_data=param_data)
        sent_request: PreparedRequest = requester._session.send.call_args_list[0][0][0]
        if expected_body is not None:
            assert sent_request.body == expected_body


@pytest.mark.parametrize(
    "provider_headers, param_headers, authenticator_headers, expected_exception, expected_headers",
    [
        # merging headers from the three sources
        ({"header": "value"}, None, None, None, {"header": "value"}),
        ({"header": "value"}, {"header2": "value"}, None, None, {"header": "value", "header2": "value"}),
        ({"header": "value"}, {"header2": "value"}, {"authheader": "val"}, None, {"header": "value", "header2": "value", "authheader": "val"}),
        # raise on conflicting headers
        ({"header": "value"}, {"header": "value"}, None, ValueError, None),
        ({"header": "value"}, None, {"header": "value"}, ValueError, None),
        ({"header": "value"}, {"header2": "value"}, {"header": "value"}, ValueError, None),
    ])
def test_send_request_headers(provider_headers, param_headers, authenticator_headers, expected_exception, expected_headers):
    # headers set by the requests framework, do not validate
    default_headers = {'User-Agent': mock.ANY, 'Accept-Encoding': mock.ANY, 'Accept': mock.ANY, 'Connection': mock.ANY}
    options_provider = MagicMock()
    options_provider.get_request_headers.return_value = provider_headers
    authenticator = MagicMock()
    authenticator.get_auth_header.return_value = authenticator_headers or {}
    requester = create_requester(authenticator=authenticator)
    requester._request_options_provider = options_provider
    if expected_exception is not None:
        with pytest.raises(expected_exception):
            requester.send_request(request_headers=param_headers)
    else:
        requester.send_request(request_headers=param_headers)
        sent_request: PreparedRequest = requester._session.send.call_args_list[0][0][0]
        assert sent_request.headers == {**default_headers, **expected_headers}


@pytest.mark.parametrize(
    "provider_params, param_params, authenticator_params, expected_exception, expected_params",
    [
        # merging params from the three sources
        ({"param": "value"}, None, None, None, {"param": "value"}),
        ({"param": "value"}, {"param2": "value"}, None, None, {"param": "value", "param2": "value"}),
        ({"param": "value"}, {"param2": "value"}, {"authparam": "val"}, None, {"param": "value", "param2": "value", "authparam": "val"}),
        # raise on conflicting params
        ({"param": "value"}, {"param": "value"}, None, ValueError, None),
        ({"param": "value"}, None, {"param": "value"}, ValueError, None),
        ({"param": "value"}, {"param2": "value"}, {"param": "value"}, ValueError, None),
    ])
def test_send_request_params(provider_params, param_params, authenticator_params, expected_exception, expected_params):
    options_provider = MagicMock()
    options_provider.get_request_params.return_value = provider_params
    authenticator = MagicMock()
    authenticator.get_request_params.return_value = authenticator_params
    requester = create_requester(authenticator=authenticator)
    requester._request_options_provider = options_provider
    if expected_exception is not None:
        with pytest.raises(expected_exception):
            requester.send_request(request_params=param_params)
    else:
        requester.send_request(request_params=param_params)
        sent_request: PreparedRequest = requester._session.send.call_args_list[0][0][0]
        parsed_url = urlparse(sent_request.url)
        query_params = {key: value[0] for key, value in parse_qs(parsed_url.query).items()}
        assert query_params == expected_params


@pytest.mark.parametrize(
    "requester_path, param_path, expected_path",
    [
        ("deals", None, "/deals"),
        ("deals", "deals2", "/deals2"),
        ("deals", "/deals2", "/deals2"),
        ("deals/{{ stream_slice.start }}/{{ next_page_token.next_page_token }}/{{ config.config_key }}/{{ parameters.param_key }}", None, "/deals/2012/pagetoken/config_value/param_value"),
    ])
def test_send_request_path(requester_path, param_path, expected_path):
    requester = create_requester(config={"config_key": "config_value"}, path=requester_path, parameters={"param_key": "param_value"})
    requester.send_request(stream_slice={"start": "2012"}, next_page_token={"next_page_token": "pagetoken"},path=param_path)
    sent_request: PreparedRequest = requester._session.send.call_args_list[0][0][0]
    parsed_url = urlparse(sent_request.url)
    assert parsed_url.path == expected_path


def test_send_request_url_base():
    requester = create_requester(url_base="https://example.org/{{ config.config_key }}/{{ parameters.param_key }}", config={"config_key": "config_value"}, parameters={"param_key": "param_value"})
    requester.send_request()
    sent_request: PreparedRequest = requester._session.send.call_args_list[0][0][0]
    assert sent_request.url == "https://example.org/config_value/param_value/deals"


def test_send_request_stream_slice_next_page_token():
    options_provider = MagicMock()
    requester = create_requester()
    requester._request_options_provider = options_provider
    stream_slice = {"id": "1234"}
    next_page_token = {"next_page_token": "next_page_token"}
    requester.send_request(stream_slice=stream_slice, next_page_token=next_page_token)
    options_provider.get_request_params.assert_called_once_with(stream_state=None, stream_slice=stream_slice, next_page_token=next_page_token)
    options_provider.get_request_body_data.assert_called_once_with(stream_state=None, stream_slice=stream_slice, next_page_token=next_page_token)
    options_provider.get_request_body_json.assert_called_once_with(stream_state=None, stream_slice=stream_slice, next_page_token=next_page_token)
    options_provider.get_request_headers.assert_called_once_with(stream_state=None, stream_slice=stream_slice, next_page_token=next_page_token)


def test_default_authenticator():
    requester = create_requester()
    assert isinstance(requester._authenticator, NoAuth)
    assert isinstance(requester._session.auth, NoAuth)


def test_token_authenticator():
    requester = create_requester(authenticator=BearerAuthenticator(token_provider=MagicMock(), config={}, parameters={}))
    assert isinstance(requester.authenticator, BearerAuthenticator)
    assert isinstance(requester._session.auth, BearerAuthenticator)


def test_stub_custom_backoff_http_stream(mocker):
    mocker.patch("time.sleep", lambda x: None)
    req = requests.Response()
    req.status_code = 429

    requester = create_requester()
    requester._backoff_time = lambda _: 0.5

    requester._session.send.return_value = req

    with pytest.raises(UserDefinedBackoffException):
        requester.send_request()
    assert requester._session.send.call_count == requester.max_retries + 1


@pytest.mark.parametrize("retries", [-20, -1, 0, 1, 2, 10])
def test_stub_custom_backoff_http_stream_retries(mocker, retries):
    mocker.patch("time.sleep", lambda x: None)
    error_handler = DefaultErrorHandler(parameters={}, config={}, max_retries=retries)
    requester = create_requester(error_handler=error_handler)
    req = requests.Response()
    req.status_code = HTTPStatus.TOO_MANY_REQUESTS
    requester._session.send.return_value = req

    with pytest.raises(UserDefinedBackoffException, match="Request URL: https://example.com/deals, Response Code: 429") as excinfo:
        requester.send_request()
    assert isinstance(excinfo.value.request, requests.PreparedRequest)
    assert isinstance(excinfo.value.response, requests.Response)
    if retries <= 0:
        assert requester._session.send.call_count == 1
    else:
        assert requester._session.send.call_count == requester.max_retries + 1


def test_stub_custom_backoff_http_stream_endless_retries(mocker):
    mocker.patch("time.sleep", lambda x: None)
    error_handler = DefaultErrorHandler(parameters={}, config={}, max_retries=None)
    requester = create_requester(error_handler=error_handler)
    req = requests.Response()
    req.status_code = HTTPStatus.TOO_MANY_REQUESTS
    infinite_number = 20

    req = requests.Response()
    req.status_code = HTTPStatus.TOO_MANY_REQUESTS
    send_mock = mocker.patch.object(requester._session, "send", side_effect=[req] * infinite_number)

    # Expecting mock object to raise a RuntimeError when the end of side_effect list parameter reached.
    with pytest.raises(StopIteration):
        requester.send_request()
    assert send_mock.call_count == infinite_number + 1


@pytest.mark.parametrize("http_code", [400, 401, 403])
def test_4xx_error_codes_http_stream(mocker, http_code):
    requester = create_requester(error_handler=DefaultErrorHandler(parameters={}, config={}, max_retries=0))
    requester._DEFAULT_RETRY_FACTOR = 0.01
    req = requests.Response()
    req.request = requests.Request()
    req.status_code = http_code
    requester._session.send.return_value = req

    with pytest.raises(ReadException):
        requester.send_request()


def test_raise_on_http_errors_off_429(mocker):
    requester = create_requester()
    requester._DEFAULT_RETRY_FACTOR = 0.01
    req = requests.Response()
    req.status_code = 429
    requester._session.send.return_value = req

    with pytest.raises(DefaultBackoffException, match="Request URL: https://example.com/deals, Response Code: 429"):
        requester.send_request()


@pytest.mark.parametrize("status_code", [500, 501, 503, 504])
def test_raise_on_http_errors_off_5xx(mocker, status_code):
    requester = create_requester()
    req = requests.Response()
    req.status_code = status_code
    requester._session.send.return_value = req
    requester._DEFAULT_RETRY_FACTOR = 0.01

    with pytest.raises(DefaultBackoffException):
        requester.send_request()
    assert requester._session.send.call_count == requester.max_retries + 1


@pytest.mark.parametrize("status_code", [400, 401, 402, 403, 416])
def test_raise_on_http_errors_off_non_retryable_4xx(mocker, status_code):
    requester = create_requester()
    req = requests.Response()
    req.status_code = status_code
    requester._session.send.return_value = req
    requester._DEFAULT_RETRY_FACTOR = 0.01

    response = requester.send_request()
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "error",
    (
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.ChunkedEncodingError,
        requests.exceptions.ReadTimeout,
    ),
)
def test_raise_on_http_errors(mocker, error):
    requester = create_requester()
    req = requests.Response()
    req.status_code = 200
    requester._session.send.return_value = req
    requester._DEFAULT_RETRY_FACTOR = 0.01
    mocker.patch.object(requester._session, "send", side_effect=error())

    with pytest.raises(error):
        requester.send_request()
    assert requester._session.send.call_count == requester.max_retries + 1


@pytest.mark.parametrize(
    "api_response, expected_message",
    [
        ({"error": "something broke"}, "something broke"),
        ({"error": {"message": "something broke"}}, "something broke"),
        ({"error": "err-001", "message": "something broke"}, "something broke"),
        ({"failure": {"message": "something broke"}}, "something broke"),
        ({"error": {"errors": [{"message": "one"}, {"message": "two"}, {"message": "three"}]}}, "one, two, three"),
        ({"errors": ["one", "two", "three"]}, "one, two, three"),
        ({"messages": ["one", "two", "three"]}, "one, two, three"),
        ({"errors": [{"message": "one"}, {"message": "two"}, {"message": "three"}]}, "one, two, three"),
        ({"error": [{"message": "one"}, {"message": "two"}, {"message": "three"}]}, "one, two, three"),
        ({"errors": [{"error": "one"}, {"error": "two"}, {"error": "three"}]}, "one, two, three"),
        ({"failures": [{"message": "one"}, {"message": "two"}, {"message": "three"}]}, "one, two, three"),
        (["one", "two", "three"], "one, two, three"),
        ([{"error": "one"}, {"error": "two"}, {"error": "three"}], "one, two, three"),
        ({"error": True}, None),
        ({"something_else": "hi"}, None),
        ({}, None),
    ],
)
def test_default_parse_response_error_message(api_response: dict, expected_message: Optional[str]):
    response = MagicMock()
    response.json.return_value = api_response

    message = HttpRequester.parse_response_error_message(response)
    assert message == expected_message


def test_default_parse_response_error_message_not_json(requests_mock):
    requests_mock.register_uri("GET", "mock://test.com/not_json", text="this is not json")
    response = requests.get("mock://test.com/not_json")

    message = HttpRequester.parse_response_error_message(response)
    assert message is None


@pytest.mark.parametrize(
    "test_name, base_url, path, expected_full_url",[
        ("test_no_slashes", "https://airbyte.io", "my_endpoint", "https://airbyte.io/my_endpoint"),
        ("test_trailing_slash_on_base_url", "https://airbyte.io/", "my_endpoint", "https://airbyte.io/my_endpoint"),
        ("test_trailing_slash_on_base_url_and_leading_slash_on_path", "https://airbyte.io/", "/my_endpoint", "https://airbyte.io/my_endpoint"),
        ("test_leading_slash_on_path", "https://airbyte.io", "/my_endpoint", "https://airbyte.io/my_endpoint"),
        ("test_trailing_slash_on_path", "https://airbyte.io", "/my_endpoint/", "https://airbyte.io/my_endpoint/"),
        ("test_nested_path_no_leading_slash", "https://airbyte.io", "v1/my_endpoint", "https://airbyte.io/v1/my_endpoint"),
        ("test_nested_path_with_leading_slash", "https://airbyte.io", "/v1/my_endpoint", "https://airbyte.io/v1/my_endpoint"),
    ]
)
def test_join_url(test_name, base_url, path, expected_full_url):
    requester = HttpRequester(
        name="name",
        url_base=base_url,
        path=path,
        http_method=HttpMethod.GET,
        request_options_provider=None,
        config={},
        parameters={},
    )
    requester._session.send = MagicMock()
    response = requests.Response()
    response.status_code = 200
    requester._session.send.return_value = response
    requester.send_request()
    sent_request: PreparedRequest = requester._session.send.call_args_list[0][0][0]
    assert sent_request.url == expected_full_url
