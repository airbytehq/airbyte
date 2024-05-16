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
import requests_cache
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator, NoAuth
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.exceptions import ReadException
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpMethod, HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from airbyte_cdk.sources.types import Config
from requests import PreparedRequest
from requests_cache import CachedResponse


@pytest.fixture
def http_requester_factory():
    def factory(
        name: str = "name",
        url_base: str = "https://test_base_url.com",
        path: str = "/",
        http_method: str = HttpMethod.GET,
        request_options_provider: Optional[InterpolatedRequestOptionsProvider] = None,
        authenticator: Optional[DeclarativeAuthenticator] = None,
        error_handler: Optional[ErrorHandler] = None,
        config: Optional[Config] = None,
        parameters: Mapping[str, Any] = None,
        disable_retries: bool = False,
        message_repository: Optional[MessageRepository] = None,
        use_cache: bool = False,
    ) -> HttpRequester:
        return HttpRequester(
            name=name,
            url_base=url_base,
            path=path,
            config=config or {},
            parameters=parameters or {},
            authenticator=authenticator,
            http_method=http_method,
            request_options_provider=request_options_provider,
            error_handler=error_handler,
            disable_retries=disable_retries,
            message_repository=message_repository or MagicMock(),
            use_cache=use_cache,
        )

    return factory


def test_http_requester():
    http_method = HttpMethod.GET

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
    assert requester.get_method() == http_method
    assert requester.get_request_params(stream_state={}, stream_slice=None, next_page_token=None) == request_params
    assert requester.get_request_body_data(stream_state={}, stream_slice=None, next_page_token=None) == request_body_data
    assert requester.get_request_body_json(stream_state={}, stream_slice=None, next_page_token=None) == request_body_json
    assert requester.interpret_response_status(requests.Response()) == response_status


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


def create_requester(
    url_base: Optional[str] = None,
    parameters: Optional[Mapping[str, Any]] = {},
    config: Optional[Config] = None,
    path: Optional[str] = None,
    authenticator: Optional[DeclarativeAuthenticator] = None,
    error_handler: Optional[ErrorHandler] = None,
) -> HttpRequester:
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
        (
            None,
            {"field": "value"},
            None,
            {"field2": "value"},
            None,
            {"authfield": "val"},
            None,
            '{"field": "value", "field2": "value", "authfield": "val"}',
        ),
        (None, {"field": "value"}, None, {"field": "value"}, None, None, ValueError, None),
        (None, {"field": "value"}, None, None, None, {"field": "value"}, ValueError, None),
        # raise on mixed data and json params
        ({"field": "value"}, {"field": "value"}, None, None, None, None, RequestBodyException, None),
        ({"field": "value"}, None, None, {"field": "value"}, None, None, RequestBodyException, None),
        (None, None, {"field": "value"}, {"field": "value"}, None, None, RequestBodyException, None),
        (None, None, None, None, {"field": "value"}, {"field": "value"}, RequestBodyException, None),
        ({"field": "value"}, None, None, None, None, {"field": "value"}, RequestBodyException, None),
    ],
)
def test_send_request_data_json(
    provider_data, provider_json, param_data, param_json, authenticator_data, authenticator_json, expected_exception, expected_body
):
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
            assert sent_request.body == expected_body.decode("UTF-8") if not isinstance(expected_body, str) else expected_body


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
        # assert body string and mapping from different source fails
        ("field=value", {"abc": "def"}, None, ValueError, None),
        ({"abc": "def"}, "field=value", None, ValueError, None),
        ("field=value", None, {"abc": "def"}, ValueError, None),
    ],
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
        (
            {"header": "value"},
            {"header2": "value"},
            {"authheader": "val"},
            None,
            {"header": "value", "header2": "value", "authheader": "val"},
        ),
        # raise on conflicting headers
        ({"header": "value"}, {"header": "value"}, None, ValueError, None),
        ({"header": "value"}, None, {"header": "value"}, ValueError, None),
        ({"header": "value"}, {"header2": "value"}, {"header": "value"}, ValueError, None),
    ],
)
def test_send_request_headers(provider_headers, param_headers, authenticator_headers, expected_exception, expected_headers):
    # headers set by the requests framework, do not validate
    default_headers = {"User-Agent": mock.ANY, "Accept-Encoding": mock.ANY, "Accept": mock.ANY, "Connection": mock.ANY}
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
    ],
)
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
    "request_parameters, config, expected_query_params",
    [
        pytest.param(
            {"k": '{"updatedDateFrom": "2023-08-20T00:00:00Z", "updatedDateTo": "2023-08-20T23:59:59Z"}'},
            {},
            "k=%7B%22updatedDateFrom%22%3A+%222023-08-20T00%3A00%3A00Z%22%2C+%22updatedDateTo%22%3A+%222023-08-20T23%3A59%3A59Z%22%7D",
            id="test-request-parameter-dictionary",
        ),
        pytest.param(
            {"k": "1,2"},
            {},
            "k=1%2C2",  # k=1,2
            id="test-request-parameter-comma-separated-numbers",
        ),
        pytest.param(
            {"k": "a,b"},
            {},
            "k=a%2Cb",  # k=a,b
            id="test-request-parameter-comma-separated-strings",
        ),
        pytest.param(
            {"k": '{{ config["k"] }}'},
            {"k": {"updatedDateFrom": "2023-08-20T00:00:00Z", "updatedDateTo": "2023-08-20T23:59:59Z"}},
            # {'updatedDateFrom': '2023-08-20T00:00:00Z', 'updatedDateTo': '2023-08-20T23:59:59Z'}
            "k=%7B%27updatedDateFrom%27%3A+%272023-08-20T00%3A00%3A00Z%27%2C+%27updatedDateTo%27%3A+%272023-08-20T23%3A59%3A59Z%27%7D",
            id="test-request-parameter-from-config-object",
        ),
        pytest.param(
            {"k": "[1,2]"},
            {},
            "k=1&k=2",
            id="test-request-parameter-list-of-numbers",
        ),
        pytest.param(
            {"k": '["a", "b"]'},
            {},
            "k=a&k=b",
            id="test-request-parameter-list-of-strings",
        ),
        pytest.param(
            {"k": '{{ config["k"] }}'},
            {"k": [1, 2]},
            "k=1&k=2",
            id="test-request-parameter-from-config-list-of-numbers",
        ),
        pytest.param(
            {"k": '{{ config["k"] }}'},
            {"k": ["a", "b"]},
            "k=a&k=b",
            id="test-request-parameter-from-config-list-of-strings",
        ),
        pytest.param(
            {"k": '{{ config["k"] }}'},
            {"k": ["a,b"]},
            "k=a%2Cb",
            id="test-request-parameter-from-config-comma-separated-strings",
        ),
        pytest.param(
            {'["a", "b"]': '{{ config["k"] }}'},
            {"k": [1, 2]},
            "%5B%22a%22%2C+%22b%22%5D=1&%5B%22a%22%2C+%22b%22%5D=2",
            id="test-key-with-list-to-be-interpolated",
        )
    ],
)
def test_request_param_interpolation(request_parameters, config, expected_query_params):
    options_provider = InterpolatedRequestOptionsProvider(
        config=config,
        request_parameters=request_parameters,
        request_body_data={},
        request_headers={},
        parameters={},
    )
    requester = create_requester()
    requester._request_options_provider = options_provider
    requester.send_request()
    sent_request: PreparedRequest = requester._session.send.call_args_list[0][0][0]
    assert sent_request.url.split("?", 1)[-1] == expected_query_params


@pytest.mark.parametrize(
    "request_parameters, config, invalid_value_for_key",
    [
        pytest.param(
            {"k": {"updatedDateFrom": "2023-08-20T00:00:00Z", "updatedDateTo": "2023-08-20T23:59:59Z"}},
            {},
            "k",
            id="test-request-parameter-object-of-the-updated-info",
        ),
        pytest.param(
            {"a": '{{ config["k"] }}', "b": {"end_timestamp": 1699109113}},
            {"k": 1699108113},
            "b",
            id="test-key-with-multiple-keys",
        ),
    ],
)
def test_request_param_interpolation_with_incorrect_values(request_parameters, config, invalid_value_for_key):
    options_provider = InterpolatedRequestOptionsProvider(
        config=config,
        request_parameters=request_parameters,
        request_body_data={},
        request_headers={},
        parameters={},
    )
    requester = create_requester()
    requester._request_options_provider = options_provider
    with pytest.raises(ValueError) as error:
        requester.send_request()

    assert (
        error.value.args[0]
        == f"Invalid value for `{invalid_value_for_key}` parameter. The values of request params cannot be an object."
    )


@pytest.mark.parametrize(
    "request_body_data, config, expected_request_body_data",
    [
        pytest.param(
            {"k": '{"updatedDateFrom": "2023-08-20T00:00:00Z", "updatedDateTo": "2023-08-20T23:59:59Z"}'},
            {},
            # k={"updatedDateFrom": "2023-08-20T00:00:00Z", "updatedDateTo": "2023-08-20T23:59:59Z"}
            "k=%7B%22updatedDateFrom%22%3A+%222023-08-20T00%3A00%3A00Z%22%2C+%22updatedDateTo%22%3A+%222023-08-20T23%3A59%3A59Z%22%7D",
            id="test-request-body-dictionary",
        ),
        pytest.param(
            {"k": "1,2"},
            {},
            "k=1%2C2",  # k=1,2
            id="test-request-body-comma-separated-numbers",
        ),
        pytest.param(
            {"k": "a,b"},
            {},
            "k=a%2Cb",  # k=a,b
            id="test-request-body-comma-separated-strings",
        ),
        pytest.param(
            {"k": "[1,2]"},
            {},
            "k=1&k=2",
            id="test-request-body-list-of-numbers",
        ),
        pytest.param(
            {"k": '["a", "b"]'},
            {},
            "k=a&k=b",
            id="test-request-body-list-of-strings",
        ),
        pytest.param(
            {"k": '{{ config["k"] }}'},
            {"k": {"updatedDateFrom": "2023-08-20T00:00:00Z", "updatedDateTo": "2023-08-20T23:59:59Z"}},
            # k={'updatedDateFrom': '2023-08-20T00:00:00Z', 'updatedDateTo': '2023-08-20T23:59:59Z'}
            "k=%7B%27updatedDateFrom%27%3A+%272023-08-20T00%3A00%3A00Z%27%2C+%27updatedDateTo%27%3A+%272023-08-20T23%3A59%3A59Z%27%7D",
            id="test-request-body-from-config-object",
        ),
        pytest.param(
            {"k": '{{ config["k"] }}'},
            {"k": [1, 2]},
            "k=1&k=2",
            id="test-request-body-from-config-list-of-numbers",
        ),
        pytest.param(
            {"k": '{{ config["k"] }}'},
            {"k": ["a", "b"]},
            "k=a&k=b",
            id="test-request-body-from-config-list-of-strings",
        ),
        pytest.param(
            {"k": '{{ config["k"] }}'},
            {"k": ["a,b"]},
            "k=a%2Cb",  # k=a,b
            id="test-request-body-from-config-comma-separated-strings",
        ),
        pytest.param(
            {'["a", "b"]': '{{ config["k"] }}'},
            {"k": [1, 2]},
            "%5B%22a%22%2C+%22b%22%5D=1&%5B%22a%22%2C+%22b%22%5D=2",  # ["a", "b"]=1&["a", "b"]=2
            id="test-key-with-list-is-not-interpolated",
        ),
        pytest.param(
            {"k": "{'updatedDateFrom': '2023-08-20T00:00:00Z', 'updatedDateTo': '2023-08-20T23:59:59Z'}"},
            {},
            # k={'updatedDateFrom': '2023-08-20T00:00:00Z', 'updatedDateTo': '2023-08-20T23:59:59Z'}
            "k=%7B%27updatedDateFrom%27%3A+%272023-08-20T00%3A00%3A00Z%27%2C+%27updatedDateTo%27%3A+%272023-08-20T23%3A59%3A59Z%27%7D",
            id="test-single-quotes-are-retained",
        ),
    ],
)
def test_request_body_interpolation(request_body_data, config, expected_request_body_data):
    options_provider = InterpolatedRequestOptionsProvider(
        config=config,
        request_parameters={},
        request_body_data=request_body_data,
        request_headers={},
        parameters={},
    )
    requester = create_requester()
    requester._request_options_provider = options_provider
    requester.send_request()
    sent_request: PreparedRequest = requester._session.send.call_args_list[0][0][0]
    assert sent_request.body == expected_request_body_data


@pytest.mark.parametrize(
    "requester_path, param_path, expected_path",
    [
        ("deals", None, "/deals"),
        ("deals", "deals2", "/deals2"),
        ("deals", "/deals2", "/deals2"),
        (
            "deals/{{ stream_slice.start }}/{{ next_page_token.next_page_token }}/{{ config.config_key }}/{{ parameters.param_key }}",
            None,
            "/deals/2012/pagetoken/config_value/param_value",
        ),
    ],
)
def test_send_request_path(requester_path, param_path, expected_path):
    requester = create_requester(config={"config_key": "config_value"}, path=requester_path, parameters={"param_key": "param_value"})
    requester.send_request(stream_slice={"start": "2012"}, next_page_token={"next_page_token": "pagetoken"}, path=param_path)
    sent_request: PreparedRequest = requester._session.send.call_args_list[0][0][0]
    parsed_url = urlparse(sent_request.url)
    assert parsed_url.path == expected_path


def test_send_request_url_base():
    requester = create_requester(
        url_base="https://example.org/{{ config.config_key }}/{{ parameters.param_key }}",
        config={"config_key": "config_value"},
        parameters={"param_key": "param_value"},
    )
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
    options_provider.get_request_params.assert_called_once_with(
        stream_state=None, stream_slice=stream_slice, next_page_token=next_page_token
    )
    options_provider.get_request_body_data.assert_called_once_with(
        stream_state=None, stream_slice=stream_slice, next_page_token=next_page_token
    )
    options_provider.get_request_body_json.assert_called_once_with(
        stream_state=None, stream_slice=stream_slice, next_page_token=next_page_token
    )
    options_provider.get_request_headers.assert_called_once_with(
        stream_state=None, stream_slice=stream_slice, next_page_token=next_page_token
    )


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
        ({"detail": {"message": "something broke"}}, "something broke"),
        ({"error": {"errors": [{"message": "one"}, {"message": "two"}, {"message": "three"}]}}, "one, two, three"),
        ({"errors": ["one", "two", "three"]}, "one, two, three"),
        ({"errors": [None, {}, "third error", 9002.09]}, "third error"),
        ({"messages": ["one", "two", "three"]}, "one, two, three"),
        ({"errors": [{"message": "one"}, {"message": "two"}, {"message": "three"}]}, "one, two, three"),
        ({"error": [{"message": "one"}, {"message": "two"}, {"message": "three"}]}, "one, two, three"),
        ({"errors": [{"error": "one"}, {"error": "two"}, {"error": "three"}]}, "one, two, three"),
        ({"failures": [{"message": "one"}, {"message": "two"}, {"message": "three"}]}, "one, two, three"),
        ({"details": [{"message": "one"}, {"message": "two"}, {"message": "three"}]}, "one, two, three"),
        ({"details": ["one", 10087, True]}, "one"),
        (["one", "two", "three"], "one, two, three"),
        ({"detail": False}, None),
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
    "test_name, base_url, path, expected_full_url",
    [
        ("test_no_slashes", "https://airbyte.io", "my_endpoint", "https://airbyte.io/my_endpoint"),
        ("test_trailing_slash_on_base_url", "https://airbyte.io/", "my_endpoint", "https://airbyte.io/my_endpoint"),
        (
            "test_trailing_slash_on_base_url_and_leading_slash_on_path",
            "https://airbyte.io/",
            "/my_endpoint",
            "https://airbyte.io/my_endpoint",
        ),
        ("test_leading_slash_on_path", "https://airbyte.io", "/my_endpoint", "https://airbyte.io/my_endpoint"),
        ("test_trailing_slash_on_path", "https://airbyte.io", "/my_endpoint/", "https://airbyte.io/my_endpoint/"),
        ("test_nested_path_no_leading_slash", "https://airbyte.io", "v1/my_endpoint", "https://airbyte.io/v1/my_endpoint"),
        ("test_nested_path_with_leading_slash", "https://airbyte.io", "/v1/my_endpoint", "https://airbyte.io/v1/my_endpoint"),
    ],
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


@pytest.mark.parametrize(
    "path, params, expected_url",
    [
        pytest.param("v1/endpoint?param1=value1", {}, "https://test_base_url.com/v1/endpoint?param1=value1", id="test_params_only_in_path"),
        pytest.param(
            "v1/endpoint", {"param1": "value1"}, "https://test_base_url.com/v1/endpoint?param1=value1", id="test_params_only_in_path"
        ),
        pytest.param("v1/endpoint", None, "https://test_base_url.com/v1/endpoint", id="test_params_is_none_and_no_params_in_path"),
        pytest.param(
            "v1/endpoint?param1=value1",
            None,
            "https://test_base_url.com/v1/endpoint?param1=value1",
            id="test_params_is_none_and_no_params_in_path",
        ),
        pytest.param(
            "v1/endpoint?param1=value1",
            {"param2": "value2"},
            "https://test_base_url.com/v1/endpoint?param1=value1&param2=value2",
            id="test_no_duplicate_params",
        ),
        pytest.param(
            "v1/endpoint?param1=value1",
            {"param1": "value1"},
            "https://test_base_url.com/v1/endpoint?param1=value1",
            id="test_duplicate_params_same_value",
        ),
        pytest.param(
            "v1/endpoint?param1=1",
            {"param1": 1},
            "https://test_base_url.com/v1/endpoint?param1=1",
            id="test_duplicate_params_same_value_not_string",
        ),
        pytest.param(
            "v1/endpoint?param1=value1",
            {"param1": "value2"},
            "https://test_base_url.com/v1/endpoint?param1=value1&param1=value2",
            id="test_duplicate_params_different_value",
        ),
    ],
)
def test_duplicate_request_params_are_deduped(path, params, expected_url):
    requester = HttpRequester(
        name="name",
        url_base="https://test_base_url.com",
        path=path,
        http_method=HttpMethod.GET,
        request_options_provider=None,
        config={},
        parameters={},
    )

    if expected_url is None:
        with pytest.raises(ValueError):
            requester._create_prepared_request(path=path, params=params)
    else:
        prepared_request = requester._create_prepared_request(path=path, params=params)
        assert prepared_request.url == expected_url


@pytest.mark.parametrize(
    "should_log, status_code, should_throw",
    [
        (True, 200, False),
        (True, 400, False),
        (True, 500, True),
        (False, 200, False),
        (False, 400, False),
        (False, 500, True),
    ],
)
def test_log_requests(should_log, status_code, should_throw):
    repository = MagicMock()
    requester = HttpRequester(
        name="name",
        url_base="https://test_base_url.com",
        path="/",
        http_method=HttpMethod.GET,
        request_options_provider=None,
        config={},
        parameters={},
        message_repository=repository,
        disable_retries=True,
    )
    requester._session.send = MagicMock()
    response = requests.Response()
    response.status_code = status_code
    requester._session.send.return_value = response
    formatter = MagicMock()
    formatter.return_value = "formatted_response"
    if should_throw:
        with pytest.raises(DefaultBackoffException):
            requester.send_request(log_formatter=formatter if should_log else None)
    else:
        requester.send_request(log_formatter=formatter if should_log else None)
    if should_log:
        assert repository.log_message.call_args_list[0].args[1]() == "formatted_response"
        formatter.assert_called_once_with(response)


def test_connection_pool():
    requester = HttpRequester(
        name="name",
        url_base="https://test_base_url.com",
        path="/",
        http_method=HttpMethod.GET,
        request_options_provider=None,
        config={},
        parameters={},
        message_repository=MagicMock(),
        disable_retries=True,
    )
    assert requester._session.adapters["https://"]._pool_connections == 20


def test_caching_filename(http_requester_factory):
    http_requester = http_requester_factory()
    assert http_requester.cache_filename == f"{http_requester.name}.sqlite"


def test_caching_session_with_enable_use_cache(http_requester_factory):
    http_requester = http_requester_factory(use_cache=True)
    assert isinstance(http_requester._session, requests_cache.CachedSession)


def test_response_caching_with_enable_use_cache(http_requester_factory, requests_mock):
    http_requester = http_requester_factory(use_cache=True)

    requests_mock.register_uri("GET", http_requester.url_base, json=[{"id": 12, "title": "test_record"}])
    http_requester.clear_cache()

    response = http_requester.send_request()

    assert requests_mock.called
    assert isinstance(response, requests.Response)

    requests_mock.reset_mock()
    new_response = http_requester.send_request()

    assert not requests_mock.called
    assert isinstance(new_response, CachedResponse)

    assert len(response.json()) == len(new_response.json())
