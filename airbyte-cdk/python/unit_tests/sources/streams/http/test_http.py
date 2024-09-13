#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
from http import HTTPStatus
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from unittest.mock import ANY, MagicMock, patch

import pytest
import requests
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, SyncMode, Type
from airbyte_cdk.sources.streams import CheckpointMixin
from airbyte_cdk.sources.streams.checkpoint import ResumableFullRefreshCursor
from airbyte_cdk.sources.streams.checkpoint.substream_resumable_full_refresh_cursor import SubstreamResumableFullRefreshCursor
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from airbyte_cdk.sources.streams.http.http_client import MessageRepresentationAirbyteTracedErrors
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class StubBasicReadHttpStream(HttpStream):
    url_base = "https://test_base_url.com"
    primary_key = ""

    def __init__(self, deduplicate_query_params: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.resp_counter = 1
        self._deduplicate_query_params = deduplicate_query_params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, **kwargs) -> str:
        return ""

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        stubResp = {"data": self.resp_counter}
        self.resp_counter += 1
        yield stubResp

    def must_deduplicate_query_params(self) -> bool:
        return self._deduplicate_query_params

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return ["updated_at"]


def test_default_authenticator():
    stream = StubBasicReadHttpStream()
    assert stream._http_client._session.auth is None


def test_requests_native_token_authenticator():
    stream = StubBasicReadHttpStream(authenticator=TokenAuthenticator("test-token"))
    assert isinstance(stream._http_client._session.auth, TokenAuthenticator)


def test_request_kwargs_used(mocker, requests_mock):
    stream = StubBasicReadHttpStream()
    request_kwargs = {"cert": None, "proxies": "google.com"}
    mocker.patch.object(stream, "request_kwargs", return_value=request_kwargs)
    send_mock = mocker.patch.object(stream._http_client._session, "send", wraps=stream._http_client._session.send)
    requests_mock.register_uri("GET", stream.url_base)

    list(stream.read_records(sync_mode=SyncMode.full_refresh))

    stream._http_client._session.send.assert_any_call(ANY, **request_kwargs)
    assert send_mock.call_count == 1


def test_stub_basic_read_http_stream_read_records(mocker):
    stream = StubBasicReadHttpStream()
    blank_response = {}  # Send a blank response is fine as we ignore the response in `parse_response anyway.
    mocker.patch.object(stream._http_client, "send_request", return_value=(None, blank_response))

    records = list(stream.read_records(SyncMode.full_refresh))

    assert [{"data": 1}] == records


class StubNextPageTokenHttpStream(StubBasicReadHttpStream):
    current_page = 0

    def __init__(self, pages: int = 5):
        super().__init__()
        self._pages = pages

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        while self.current_page < self._pages:
            page_token = {"page": self.current_page}
            self.current_page += 1
            return page_token
        return None


def test_next_page_token_is_input_to_other_methods(mocker):
    """Validates that the return value from next_page_token is passed into other methods that need it like request_params, headers, body, etc.."""
    pages = 5
    stream = StubNextPageTokenHttpStream(pages=pages)
    blank_response = {}  # Send a blank response is fine as we ignore the response in `parse_response anyway.
    mocker.patch.object(stream._http_client, "send_request", return_value=(None, blank_response))

    methods = ["request_params", "request_headers", "request_body_json"]
    for method in methods:
        # Wrap all methods we're interested in testing with mocked objects so we can later spy on their input args and verify they were what we expect
        mocker.patch.object(stream, method, wraps=getattr(stream, method))

    records = list(stream.read_records(SyncMode.full_refresh))

    # Since we have 5 pages, we expect 5 tokens which are {"page":1}, {"page":2}, etc...
    expected_next_page_tokens = [{"page": i} for i in range(pages)]
    for method in methods:
        # First assert that they were called with no next_page_token. This is the first call in the pagination loop.
        getattr(stream, method).assert_any_call(next_page_token=None, stream_slice=None, stream_state={})
        for token in expected_next_page_tokens:
            # Then verify that each method
            getattr(stream, method).assert_any_call(next_page_token=token, stream_slice=None, stream_state={})

    expected = [{"data": 1}, {"data": 2}, {"data": 3}, {"data": 4}, {"data": 5}, {"data": 6}]

    assert records == expected


class StubBadUrlHttpStream(StubBasicReadHttpStream):
    url_base = "bad_url"


def test_stub_bad_url_http_stream_read_records(mocker):
    stream = StubBadUrlHttpStream()

    with pytest.raises(requests.exceptions.RequestException):
        list(stream.read_records(SyncMode.full_refresh))


class StubCustomBackoffHttpStream(StubBasicReadHttpStream):
    def backoff_time(self, response: requests.Response) -> Optional[float]:
        return 0.5


def test_stub_custom_backoff_http_stream(mocker):
    mocker.patch("time.sleep", lambda x: None)
    stream = StubCustomBackoffHttpStream()
    req = requests.Response()
    req.status_code = 429

    send_mock = mocker.patch.object(requests.Session, "send", return_value=req)

    with pytest.raises(UserDefinedBackoffException):
        list(stream.read_records(SyncMode.full_refresh))
    assert send_mock.call_count == stream.max_retries + 1

    # TODO(davin): Figure out how to assert calls.


@pytest.mark.parametrize("retries", [-20, -1, 0, 1, 2, 10])
def test_stub_custom_backoff_http_stream_retries(mocker, retries):
    mocker.patch("time.sleep", lambda x: None)

    class StubCustomBackoffHttpStreamRetries(StubCustomBackoffHttpStream):
        @property
        def max_retries(self):
            return retries

        def get_error_handler(self) -> Optional[ErrorHandler]:
            return HttpStatusErrorHandler(logging.Logger, max_retries=retries)

    stream = StubCustomBackoffHttpStreamRetries()
    req = requests.Response()
    req.status_code = HTTPStatus.TOO_MANY_REQUESTS
    send_mock = mocker.patch.object(requests.Session, "send", return_value=req)

    with pytest.raises(UserDefinedBackoffException, match="Too many requests") as excinfo:
        list(stream.read_records(SyncMode.full_refresh))
    assert isinstance(excinfo.value.request, requests.PreparedRequest)
    assert isinstance(excinfo.value.response, requests.Response)
    if retries <= 0:
        assert send_mock.call_count == 1
    else:
        assert send_mock.call_count == stream.max_retries + 1


def test_stub_custom_backoff_http_stream_endless_retries(mocker):
    mocker.patch("time.sleep", lambda x: None)

    class StubCustomBackoffHttpStreamRetries(StubCustomBackoffHttpStream):
        def get_error_handler(self) -> Optional[ErrorHandler]:
            return HttpStatusErrorHandler(logging.Logger, max_retries=99999)

    infinite_number = 20

    stream = StubCustomBackoffHttpStreamRetries()
    req = requests.Response()
    req.status_code = HTTPStatus.TOO_MANY_REQUESTS
    send_mock = mocker.patch.object(requests.Session, "send", side_effect=[req] * infinite_number)

    # Expecting mock object to raise a RuntimeError when the end of side_effect list parameter reached.
    with pytest.raises(RuntimeError):
        list(stream.read_records(SyncMode.full_refresh))
    assert send_mock.call_count == infinite_number + 1


@pytest.mark.parametrize("http_code", [400, 401, 403])
def test_4xx_error_codes_http_stream(mocker, http_code):
    stream = StubCustomBackoffHttpStream()
    req = requests.Response()
    req.status_code = http_code
    mocker.patch.object(requests.Session, "send", return_value=req)

    with pytest.raises(MessageRepresentationAirbyteTracedErrors):
        list(stream.read_records(SyncMode.full_refresh))


class AutoFailFalseHttpStream(StubBasicReadHttpStream):
    raise_on_http_errors = False
    max_retries = 3

    def get_error_handler(self) -> Optional[ErrorHandler]:
        return HttpStatusErrorHandler(logging.getLogger(), max_retries=3)


def test_raise_on_http_errors_off_429(mocker):
    mocker.patch("time.sleep", lambda x: None)
    stream = AutoFailFalseHttpStream()
    req = requests.Response()
    req.status_code = 429

    mocker.patch.object(requests.Session, "send", return_value=req)
    with pytest.raises(DefaultBackoffException, match="Too many requests"):
        stream.exit_on_rate_limit = True
        list(stream.read_records(SyncMode.full_refresh))


@pytest.mark.parametrize("status_code", [500, 501, 503, 504])
def test_raise_on_http_errors_off_5xx(mocker, status_code):
    mocker.patch("time.sleep", lambda x: None)
    stream = AutoFailFalseHttpStream()
    req = requests.Response()
    req.status_code = status_code

    send_mock = mocker.patch.object(requests.Session, "send", return_value=req)
    with pytest.raises(DefaultBackoffException):
        list(stream.read_records(SyncMode.full_refresh))
    assert send_mock.call_count == stream.max_retries + 1


@pytest.mark.parametrize("status_code", [400, 401, 402, 403, 416])
def test_raise_on_http_errors_off_non_retryable_4xx(mocker, status_code):
    stream = AutoFailFalseHttpStream()
    req = requests.PreparedRequest()
    res = requests.Response()
    res.status_code = status_code

    mocker.patch.object(requests.Session, "send", return_value=res)
    response = stream._http_client._session.send(req)
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
    mocker.patch("time.sleep", lambda x: None)
    stream = AutoFailFalseHttpStream()
    send_mock = mocker.patch.object(requests.Session, "send", side_effect=error())

    with pytest.raises(DefaultBackoffException):
        list(stream.read_records(SyncMode.full_refresh))
    assert send_mock.call_count == stream.max_retries + 1


class PostHttpStream(StubBasicReadHttpStream):
    http_method = "POST"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """Returns response data as is"""
        yield response.json()


class TestRequestBody:
    """Suite of different tests for request bodies"""

    json_body = {"key": "value"}
    data_body = "key:value"
    form_body = {"key1": "value1", "key2": 1234}
    urlencoded_form_body = "key1=value1&key2=1234"

    def request2response(self, request, context):
        return json.dumps({"body": request.text, "content_type": request.headers.get("Content-Type")})

    def test_json_body(self, mocker, requests_mock):

        stream = PostHttpStream()
        mocker.patch.object(stream, "request_body_json", return_value=self.json_body)

        requests_mock.register_uri("POST", stream.url_base, text=self.request2response)
        response = list(stream.read_records(sync_mode=SyncMode.full_refresh))[0]

        assert response["content_type"] == "application/json"
        assert json.loads(response["body"]) == self.json_body

    def test_text_body(self, mocker, requests_mock):

        stream = PostHttpStream()
        mocker.patch.object(stream, "request_body_data", return_value=self.data_body)

        requests_mock.register_uri("POST", stream.url_base, text=self.request2response)
        response = list(stream.read_records(sync_mode=SyncMode.full_refresh))[0]

        assert response["content_type"] is None
        assert response["body"] == self.data_body

    def test_form_body(self, mocker, requests_mock):

        stream = PostHttpStream()
        mocker.patch.object(stream, "request_body_data", return_value=self.form_body)

        requests_mock.register_uri("POST", stream.url_base, text=self.request2response)
        response = list(stream.read_records(sync_mode=SyncMode.full_refresh))[0]

        assert response["content_type"] == "application/x-www-form-urlencoded"
        assert response["body"] == self.urlencoded_form_body

    def test_text_json_body(self, mocker, requests_mock):
        """checks a exception if both functions were overridden"""
        stream = PostHttpStream()
        mocker.patch.object(stream, "request_body_data", return_value=self.data_body)
        mocker.patch.object(stream, "request_body_json", return_value=self.json_body)
        requests_mock.register_uri("POST", stream.url_base, text=self.request2response)
        with pytest.raises(RequestBodyException):
            list(stream.read_records(sync_mode=SyncMode.full_refresh))

    def test_body_for_all_methods(self, mocker, requests_mock):
        """Stream must send a body for GET/POST/PATCH/PUT methods only"""
        stream = PostHttpStream()
        methods = {
            "POST": True,
            "PUT": True,
            "PATCH": True,
            "GET": True,
            "DELETE": False,
            "OPTIONS": False,
        }
        for method, with_body in methods.items():
            stream.http_method = method
            mocker.patch.object(stream, "request_body_data", return_value=self.data_body)
            requests_mock.register_uri(method, stream.url_base, text=self.request2response)
            response = list(stream.read_records(sync_mode=SyncMode.full_refresh))[0]
            if with_body:
                assert response["body"] == self.data_body
            else:
                assert response["body"] is None


class CacheHttpStream(StubBasicReadHttpStream):
    use_cache = True

    def get_json_schema(self) -> Mapping[str, Any]:
        return {}


class CacheHttpSubStream(HttpSubStream):
    url_base = "https://example.com"
    primary_key = ""

    def __init__(self, parent):
        super().__init__(parent=parent)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return []

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, **kwargs) -> str:
        return ""


def test_caching_filename():
    stream = CacheHttpStream()
    assert stream.cache_filename == f"{stream.name}.sqlite"


def test_caching_sessions_are_different():
    stream_1 = CacheHttpStream()
    stream_2 = CacheHttpStream()

    assert stream_1._http_client._session != stream_2._http_client._session
    assert stream_1.cache_filename == stream_2.cache_filename


# def test_cached_streams_wortk_when_request_path_is_not_set(mocker, requests_mock):
# This test verifies that HttpStreams with a cached session work even if the path is not set
# For instance, when running in a unit test
# stream = CacheHttpStream()
# with mocker.patch.object(stream._session, "send", wraps=stream._session.send):
#     requests_mock.register_uri("GET", stream.url_base)
#     records = list(stream.read_records(sync_mode=SyncMode.full_refresh))
#     assert records == [{"data": 1}]
# ""


def test_parent_attribute_exist():
    parent_stream = CacheHttpStream()
    child_stream = CacheHttpSubStream(parent=parent_stream)

    assert child_stream.parent == parent_stream


def test_that_response_was_cached(mocker, requests_mock):
    requests_mock.register_uri("GET", "https://google.com/", text="text")
    stream = CacheHttpStream()
    stream._http_client.clear_cache()
    mocker.patch.object(stream, "url_base", "https://google.com/")
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh))

    assert requests_mock.called

    requests_mock.reset_mock()
    new_records = list(stream.read_records(sync_mode=SyncMode.full_refresh))

    assert len(records) == len(new_records)
    assert not requests_mock.called


class CacheHttpStreamWithSlices(CacheHttpStream):
    paths = ["", "search"]

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f'{stream_slice["path"]}' if stream_slice else ""

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for path in self.paths:
            yield {"path": path}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {"value": len(response.text)}


@patch("airbyte_cdk.sources.streams.core.logging", MagicMock())
def test_using_cache(mocker, requests_mock):
    requests_mock.register_uri("GET", "https://google.com/", text="text")
    requests_mock.register_uri("GET", "https://google.com/search", text="text")

    parent_stream = CacheHttpStreamWithSlices()
    mocker.patch.object(parent_stream, "url_base", "https://google.com/")
    parent_stream._http_client._session.cache.clear()

    assert requests_mock.call_count == 0
    assert len(parent_stream._http_client._session.cache.responses) == 0

    for _slice in parent_stream.stream_slices():
        list(parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=_slice))

    assert requests_mock.call_count == 2
    assert len(parent_stream._http_client._session.cache.responses) == 2

    child_stream = CacheHttpSubStream(parent=parent_stream)

    for _slice in child_stream.stream_slices(sync_mode=SyncMode.full_refresh):
        pass

    assert requests_mock.call_count == 2
    assert len(parent_stream._http_client._session.cache.responses) == 2
    assert parent_stream._http_client._session.cache.contains(url="https://google.com/")
    assert parent_stream._http_client._session.cache.contains(url="https://google.com/search")


class AutoFailTrueHttpStream(StubBasicReadHttpStream):
    raise_on_http_errors = True

    def should_retry(self, *args, **kwargs):
        return True


@pytest.mark.parametrize(
    "response_status_code,should_retry, raise_on_http_errors, expected_response_action",
    [
        (300, True, True, ResponseAction.RETRY),
        (200, False, True, ResponseAction.SUCCESS),
        (503, False, True, ResponseAction.FAIL),
        (503, False, False, ResponseAction.IGNORE),
    ],
)
def test_http_stream_adapter_http_status_error_handler_should_retry_false_raise_on_http_errors(
    mocker, response_status_code: int, should_retry: bool, raise_on_http_errors: bool, expected_response_action: ResponseAction
):
    stream = AutoFailTrueHttpStream()
    mocker.patch.object(stream, "should_retry", return_value=should_retry)
    mocker.patch.object(stream, "raise_on_http_errors", raise_on_http_errors)
    res = requests.Response()
    res.status_code = response_status_code
    error_handler = stream.get_error_handler()
    error_resolution = error_handler.interpret_response(res)
    assert error_resolution.response_action == expected_response_action


@pytest.mark.parametrize("status_code", range(400, 600))
def test_send_raise_on_http_errors_logs(mocker, status_code):
    mocker.patch("time.sleep", lambda x: None)
    stream = AutoFailTrueHttpStream()
    res = requests.Response()
    res.status_code = status_code
    mocker.patch.object(requests.Session, "send", return_value=res)
    mocker.patch.object(stream._http_client, "_logger")
    with pytest.raises(requests.exceptions.HTTPError):
        response = stream._http_client.send_request("GET", "https://g", {}, exit_on_rate_limit=True)
        stream._http_client.logger.error.assert_called_with(response.text)
        assert response.status_code == status_code


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
    stream = StubBasicReadHttpStream()
    response = MagicMock()
    response.json.return_value = api_response

    message = stream.parse_response_error_message(response)
    assert message == expected_message


def test_default_parse_response_error_message_not_json(requests_mock):
    stream = StubBasicReadHttpStream()
    requests_mock.register_uri("GET", "mock://test.com/not_json", text="this is not json")
    response = requests.get("mock://test.com/not_json")

    message = stream.parse_response_error_message(response)
    assert message is None


def test_default_get_error_display_message_handles_http_error(mocker):
    stream = StubBasicReadHttpStream()
    mocker.patch.object(stream, "parse_response_error_message", return_value="my custom message")

    non_http_err_msg = stream.get_error_display_message(RuntimeError("not me"))
    assert non_http_err_msg is None

    response = requests.Response()
    http_exception = requests.HTTPError(response=response)
    http_err_msg = stream.get_error_display_message(http_exception)
    assert http_err_msg == "my custom message"


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
    actual_url = HttpStream._join_url(base_url, path)
    assert actual_url == expected_full_url


@pytest.mark.parametrize(
    "deduplicate_query_params, path, params, expected_url",
    [
        pytest.param(
            True, "v1/endpoint?param1=value1", {}, "https://test_base_url.com/v1/endpoint?param1=value1", id="test_params_only_in_path"
        ),
        pytest.param(
            True, "v1/endpoint", {"param1": "value1"}, "https://test_base_url.com/v1/endpoint?param1=value1", id="test_params_only_in_path"
        ),
        pytest.param(True, "v1/endpoint", None, "https://test_base_url.com/v1/endpoint", id="test_params_is_none_and_no_params_in_path"),
        pytest.param(
            True,
            "v1/endpoint?param1=value1",
            None,
            "https://test_base_url.com/v1/endpoint?param1=value1",
            id="test_params_is_none_and_no_params_in_path",
        ),
        pytest.param(
            True,
            "v1/endpoint?param1=value1",
            {"param2": "value2"},
            "https://test_base_url.com/v1/endpoint?param1=value1&param2=value2",
            id="test_no_duplicate_params",
        ),
        pytest.param(
            True,
            "v1/endpoint?param1=value1",
            {"param1": "value1"},
            "https://test_base_url.com/v1/endpoint?param1=value1",
            id="test_duplicate_params_same_value",
        ),
        pytest.param(
            True,
            "v1/endpoint?param1=1",
            {"param1": 1},
            "https://test_base_url.com/v1/endpoint?param1=1",
            id="test_duplicate_params_same_value_not_string",
        ),
        pytest.param(
            True,
            "v1/endpoint?param1=value1",
            {"param1": "value2"},
            "https://test_base_url.com/v1/endpoint?param1=value1&param1=value2",
            id="test_duplicate_params_different_value",
        ),
        pytest.param(
            False,
            "v1/endpoint?param1=value1",
            {"param1": "value2"},
            "https://test_base_url.com/v1/endpoint?param1=value1&param1=value2",
            id="test_same_params_different_value_no_deduplication",
        ),
        pytest.param(
            False,
            "v1/endpoint?param1=value1",
            {"param1": "value1"},
            "https://test_base_url.com/v1/endpoint?param1=value1&param1=value1",
            id="test_same_params_same_value_no_deduplication",
        ),
    ],
)
def test_duplicate_request_params_are_deduped(deduplicate_query_params, path, params, expected_url):

    stream = StubBasicReadHttpStream(deduplicate_query_params)

    if expected_url is None:
        with pytest.raises(ValueError):
            stream._http_client._create_prepared_request(
                http_method=stream.http_method,
                url=stream._join_url(stream.url_base, path),
                params=params,
                dedupe_query_params=deduplicate_query_params,
            )
    else:
        prepared_request = stream._http_client._create_prepared_request(
            http_method=stream.http_method,
            url=stream._join_url(stream.url_base, path),
            params=params,
            dedupe_query_params=deduplicate_query_params,
        )
        assert prepared_request.url == expected_url


def test_connection_pool():
    stream = StubBasicReadHttpStream(authenticator=TokenAuthenticator("test-token"))
    assert stream._http_client._session.adapters["https://"]._pool_connections == 20


class StubParentHttpStream(HttpStream, CheckpointMixin):
    primary_key = "primary_key"

    counter = 0

    def __init__(self, records: List[Mapping[str, Any]]):
        super().__init__()
        self._records = records
        self._state: MutableMapping[str, Any] = {}

    @property
    def url_base(self) -> str:
        return "https://airbyte.io/api/v1"

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "/stub"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return {"__ab_full_refresh_sync_complete": True}

    def _read_single_page(
        self,
        records_generator_fn: Callable[
            [requests.PreparedRequest, requests.Response, Mapping[str, Any], Optional[Mapping[str, Any]]], Iterable[StreamData]
        ],
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        yield from self._records

        self.state = {"__ab_full_refresh_sync_complete": True}

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        return []

    def get_json_schema(self) -> Mapping[str, Any]:
        return {}


class StubParentResumableFullRefreshStream(HttpStream, CheckpointMixin):
    primary_key = "primary_key"

    counter = 0

    def __init__(self, record_pages: List[List[Mapping[str, Any]]]):
        super().__init__()
        self._record_pages = record_pages
        self._state: MutableMapping[str, Any] = {}

    @property
    def url_base(self) -> str:
        return "https://airbyte.io/api/v1"

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "/stub"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return {"__ab_full_refresh_sync_complete": True}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        page_number = self.state.get("page") or 1
        yield from self._record_pages[page_number - 1]

        if page_number < len(self._record_pages):
            self.state = {"page": page_number + 1}
        else:
            self.state = {"__ab_full_refresh_sync_complete": True}

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        return []

    def get_json_schema(self) -> Mapping[str, Any]:
        return {}


class StubHttpSubstream(HttpSubStream):
    primary_key = "primary_key"

    @property
    def url_base(self) -> str:
        return "https://airbyte.io/api/v1"

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "/stub"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def _read_pages(
        self,
        records_generator_fn: Callable[
            [requests.PreparedRequest, requests.Response, Mapping[str, Any], Optional[Mapping[str, Any]]], Iterable[StreamData]
        ],
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        return [
            {"id": "abc", "parent": stream_slice.get("id")},
            {"id", "def", "parent", stream_slice.get("id")},
        ]

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        return []


def test_substream_with_incremental_parent():
    expected_slices = [
        {"parent": {"id": "abc"}},
        {"parent": {"id": "def"}},
    ]

    parent_records = [
        {"id": "abc"},
        {"id": "def"},
    ]

    parent_stream = StubParentHttpStream(records=parent_records)
    substream = StubHttpSubstream(parent=parent_stream)

    actual_slices = [slice for slice in substream.stream_slices(sync_mode=SyncMode.full_refresh)]
    assert actual_slices == expected_slices


def test_substream_with_resumable_full_refresh_parent():
    parent_pages = [
        [
            {"id": "page_1_abc"},
            {"id": "page_1_def"},
        ],
        [
            {"id": "page_2_abc"},
            {"id": "page_2_def"},
        ],
        [
            {"id": "page_3_abc"},
            {"id": "page_3_def"},
        ],
    ]

    expected_slices = [
        {"parent": {"id": "page_1_abc"}},
        {"parent": {"id": "page_1_def"}},
        {"parent": {"id": "page_2_abc"}},
        {"parent": {"id": "page_2_def"}},
        {"parent": {"id": "page_3_abc"}},
        {"parent": {"id": "page_3_def"}},
    ]

    parent_stream = StubParentResumableFullRefreshStream(record_pages=parent_pages)
    substream = StubHttpSubstream(parent=parent_stream)

    actual_slices = [slice for slice in substream.stream_slices(sync_mode=SyncMode.full_refresh)]
    assert actual_slices == expected_slices


def test_substream_skips_non_record_messages():
    expected_slices = [
        {"parent": {"id": "abc"}},
        {"parent": {"id": "def"}},
        {"parent": {"id": "ghi"}},
    ]

    parent_records = [
        {"id": "abc"},
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="should_not_be_parent_record")),
        {"id": "def"},
        {"id": "ghi"},
    ]

    parent_stream = StubParentHttpStream(records=parent_records)
    substream = StubHttpSubstream(parent=parent_stream)

    actual_slices = [slice for slice in substream.stream_slices(sync_mode=SyncMode.full_refresh)]
    assert actual_slices == expected_slices


class StubFullRefreshHttpStream(HttpStream):
    url_base = "https://test_base_url.com"
    primary_key = "id"

    def __init__(self, deduplicate_query_params: bool = False, pages: int = 5, **kwargs):
        super().__init__(**kwargs)
        self._pages_request_count = 0
        self._page_counter = 0
        self.resp_counter = 0
        self._deduplicate_query_params = deduplicate_query_params
        self._pages = pages

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        current_page = self.cursor.get_stream_state().get("page", 1)
        if current_page < self._pages:
            current_page += 1
            page_token = {"page": current_page}
            return page_token
        return None

    def path(self, **kwargs) -> str:
        return ""

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        self.resp_counter += 1
        stubResp = {"data": self.resp_counter}
        yield stubResp

    def must_deduplicate_query_params(self) -> bool:
        return self._deduplicate_query_params


class StubFullRefreshLegacySliceHttpStream(StubFullRefreshHttpStream):
    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from [{}]


def test_resumable_full_refresh_read_from_start(mocker):
    """
    Validates the default behavior of a stream that supports resumable full refresh by using read_records() which gets one
    page per invocation and emits state afterward.
    parses over
    """
    pages = 5
    stream = StubFullRefreshHttpStream(pages=pages)
    blank_response = {}  # Send a blank response is fine as we ignore the response in `parse_response anyway.
    mocker.patch.object(stream._http_client, "send_request", return_value=(None, blank_response))

    # Wrap all methods we're interested in testing with mocked objects to spy on their input args and verify they were what we expect
    mocker.patch.object(stream, "_read_single_page", wraps=getattr(stream, "_read_single_page"))
    methods = ["request_params", "request_headers", "request_body_json"]
    for method in methods:
        mocker.patch.object(stream, method, wraps=getattr(stream, method))

    checkpoint_reader = stream._get_checkpoint_reader(
        cursor_field=[], logger=logging.getLogger("airbyte"), sync_mode=SyncMode.full_refresh, stream_state={}
    )
    next_stream_slice = checkpoint_reader.next()
    records = []

    expected_checkpoints = [{"page": 2}, {"page": 3}, {"page": 4}, {"page": 5}, {"__ab_full_refresh_sync_complete": True}]
    i = 0
    while next_stream_slice is not None:
        next_records = list(stream.read_records(SyncMode.full_refresh, stream_slice=next_stream_slice))
        records.extend(next_records)
        checkpoint_reader.observe(stream.state)
        assert checkpoint_reader.get_checkpoint() == expected_checkpoints[i]
        next_stream_slice = checkpoint_reader.next()
        i += 1

    assert getattr(stream, "_read_single_page").call_count == 5

    # Since we have 5 pages, and we don't pass in the first page, we expect 4 tokens starting at {"page":2}, {"page":3}, etc...
    expected_next_page_tokens = expected_checkpoints[:4]
    for method in methods:
        # First assert that they were called with no next_page_token. This is the first call in the pagination loop.
        getattr(stream, method).assert_any_call(next_page_token=None, stream_slice={}, stream_state={})
        for token in expected_next_page_tokens:
            # Then verify that each method
            getattr(stream, method).assert_any_call(next_page_token=token, stream_slice=token, stream_state={})

    expected = [{"data": 1}, {"data": 2}, {"data": 3}, {"data": 4}, {"data": 5}]

    assert records == expected


def test_resumable_full_refresh_read_from_state(mocker):
    """
    Validates the default behavior of a stream that supports resumable full refresh with an incoming state by using
    read_records() which gets one page per invocation and emits state afterward.
    parses over
    """
    pages = 5
    stream = StubFullRefreshHttpStream(pages=pages)
    blank_response = {}  # Send a blank response is fine as we ignore the response in `parse_response anyway.
    mocker.patch.object(stream._http_client, "send_request", return_value=(None, blank_response))

    # Wrap all methods we're interested in testing with mocked objects to spy on their input args and verify they were what we expect
    mocker.patch.object(stream, "_read_single_page", wraps=getattr(stream, "_read_single_page"))
    methods = ["request_params", "request_headers", "request_body_json"]
    for method in methods:
        mocker.patch.object(stream, method, wraps=getattr(stream, method))

    checkpoint_reader = stream._get_checkpoint_reader(
        cursor_field=[], logger=logging.getLogger("airbyte"), sync_mode=SyncMode.full_refresh, stream_state={"page": 3}
    )
    next_stream_slice = checkpoint_reader.next()
    records = []

    expected_checkpoints = [{"page": 4}, {"page": 5}, {"__ab_full_refresh_sync_complete": True}]
    i = 0
    while next_stream_slice is not None:
        next_records = list(stream.read_records(SyncMode.full_refresh, stream_slice=next_stream_slice))
        records.extend(next_records)
        checkpoint_reader.observe(stream.state)
        assert checkpoint_reader.get_checkpoint() == expected_checkpoints[i]
        next_stream_slice = checkpoint_reader.next()
        i += 1

    assert getattr(stream, "_read_single_page").call_count == 3

    # Since we start at page 3, we expect 3 tokens starting at {"page":3}, {"page":4}, etc...
    expected_next_page_tokens = [{"page": 3}, {"page": 4}, {"page": 5}]
    for method in methods:
        for token in expected_next_page_tokens:
            # Then verify that each method
            getattr(stream, method).assert_any_call(next_page_token=token, stream_slice=token, stream_state={})

    expected = [{"data": 1}, {"data": 2}, {"data": 3}]

    assert records == expected


def test_resumable_full_refresh_legacy_stream_slice(mocker):
    """
    Validates the default behavior of a stream that supports resumable full refresh where incoming stream slices use the
    legacy Mapping format
    """
    pages = 5
    stream = StubFullRefreshLegacySliceHttpStream(pages=pages)
    blank_response = {}  # Send a blank response is fine as we ignore the response in `parse_response anyway.
    mocker.patch.object(stream._http_client, "send_request", return_value=(None, blank_response))

    # Wrap all methods we're interested in testing with mocked objects to spy on their input args and verify they were what we expect
    mocker.patch.object(stream, "_read_single_page", wraps=getattr(stream, "_read_single_page"))
    methods = ["request_params", "request_headers", "request_body_json"]
    for method in methods:
        mocker.patch.object(stream, method, wraps=getattr(stream, method))

    checkpoint_reader = stream._get_checkpoint_reader(
        cursor_field=[], logger=logging.getLogger("airbyte"), sync_mode=SyncMode.full_refresh, stream_state={"page": 2}
    )
    next_stream_slice = checkpoint_reader.next()
    records = []

    expected_checkpoints = [{"page": 3}, {"page": 4}, {"page": 5}, {"__ab_full_refresh_sync_complete": True}]
    i = 0
    while next_stream_slice is not None:
        next_records = list(stream.read_records(SyncMode.full_refresh, stream_slice=next_stream_slice))
        records.extend(next_records)
        checkpoint_reader.observe(stream.state)
        assert checkpoint_reader.get_checkpoint() == expected_checkpoints[i]
        next_stream_slice = checkpoint_reader.next()
        i += 1

    assert getattr(stream, "_read_single_page").call_count == 4

    # Since we start at page 3, we expect 3 tokens starting at {"page":3}, {"page":4}, etc...
    expected_next_page_tokens = [{"page": 2}, {"page": 3}, {"page": 4}, {"page": 5}]
    for method in methods:
        for token in expected_next_page_tokens:
            # Then verify that each method
            getattr(stream, method).assert_any_call(next_page_token=token, stream_slice=token, stream_state={})

    expected = [{"data": 1}, {"data": 2}, {"data": 3}, {"data": 4}]

    assert records == expected


class StubSubstreamResumableFullRefreshStream(HttpSubStream, CheckpointMixin):
    primary_key = "primary_key"

    counter = 0

    def __init__(self, parent: HttpStream, partition_id_to_child_records: Mapping[str, List[Mapping[str, Any]]]):
        super().__init__(parent=parent)
        self._partition_id_to_child_records = partition_id_to_child_records
        # self._state: MutableMapping[str, Any] = {}

    @property
    def url_base(self) -> str:
        return "https://airbyte.io/api/v1"

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return f"/parents/{stream_slice.get('parent_id')}/children"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    # def read_records(
    #         self,
    #         sync_mode: SyncMode,
    #         cursor_field: Optional[List[str]] = None,
    #         stream_slice: Optional[Mapping[str, Any]] = None,
    #         stream_state: Optional[Mapping[str, Any]] = None,
    # ) -> Iterable[StreamData]:
    #     page_number = self.state.get("page") or 1
    #     yield from self._record_pages[page_number - 1]
    #
    #     if page_number < len(self._record_pages):
    #         self.state = {"page": page_number + 1}
    #     else:
    #         self.state = {"__ab_full_refresh_sync_complete": True}

    def _fetch_next_page(
        self,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        return requests.PreparedRequest(), requests.Response()

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        partition_id = stream_slice.get("parent").get("parent_id")
        if partition_id in self._partition_id_to_child_records:
            yield from self._partition_id_to_child_records.get(partition_id)
        else:
            raise Exception(f"No mocked output supplied for parent partition_id: {partition_id}")

    def get_json_schema(self) -> Mapping[str, Any]:
        return {}


def test_substream_resumable_full_refresh_read_from_start(mocker):
    """
    Validates the default behavior of a stream that supports resumable full refresh by using read_records() which gets one
    page per invocation and emits state afterward.
    parses over
    """

    parent_records = [
        {"parent_id": "100", "name": "christopher_nolan"},
        {"parent_id": "101", "name": "celine_song"},
        {"parent_id": "102", "name": "david_fincher"},
    ]
    parent_stream = StubParentHttpStream(records=parent_records)

    parents_to_children_records = {
        "100": [
            {"id": "a200", "parent_id": "100", "film": "interstellar"},
            {"id": "a201", "parent_id": "100", "film": "oppenheimer"},
            {"id": "a202", "parent_id": "100", "film": "inception"},
        ],
        "101": [{"id": "b200", "parent_id": "101", "film": "past_lives"}, {"id": "b201", "parent_id": "101", "film": "materialists"}],
        "102": [
            {"id": "c200", "parent_id": "102", "film": "the_social_network"},
            {"id": "c201", "parent_id": "102", "film": "gone_girl"},
            {"id": "c202", "parent_id": "102", "film": "the_curious_case_of_benjamin_button"},
        ],
    }
    stream = StubSubstreamResumableFullRefreshStream(parent=parent_stream, partition_id_to_child_records=parents_to_children_records)

    blank_response = {}  # Send a blank response is fine as we ignore the response in `parse_response anyway.
    mocker.patch.object(stream._http_client, "send_request", return_value=(None, blank_response))

    # Wrap all methods we're interested in testing with mocked objects to spy on their input args and verify they were what we expect
    mocker.patch.object(stream, "_read_pages", wraps=getattr(stream, "_read_pages"))

    checkpoint_reader = stream._get_checkpoint_reader(
        cursor_field=[], logger=logging.getLogger("airbyte"), sync_mode=SyncMode.full_refresh, stream_state={}
    )
    next_stream_slice = checkpoint_reader.next()
    records = []

    expected_checkpoints = [
        {
            "states": [
                {
                    "cursor": {"__ab_full_refresh_sync_complete": True},
                    "partition": {"parent": {"name": "christopher_nolan", "parent_id": "100"}},
                }
            ]
        },
        {
            "states": [
                {
                    "cursor": {"__ab_full_refresh_sync_complete": True},
                    "partition": {"parent": {"name": "christopher_nolan", "parent_id": "100"}},
                },
                {"cursor": {"__ab_full_refresh_sync_complete": True}, "partition": {"parent": {"name": "celine_song", "parent_id": "101"}}},
            ]
        },
        {
            "states": [
                {
                    "cursor": {"__ab_full_refresh_sync_complete": True},
                    "partition": {"parent": {"name": "christopher_nolan", "parent_id": "100"}},
                },
                {"cursor": {"__ab_full_refresh_sync_complete": True}, "partition": {"parent": {"name": "celine_song", "parent_id": "101"}}},
                {
                    "cursor": {"__ab_full_refresh_sync_complete": True},
                    "partition": {"parent": {"name": "david_fincher", "parent_id": "102"}},
                },
            ]
        },
    ]

    i = 0
    while next_stream_slice is not None:
        next_records = list(stream.read_records(SyncMode.full_refresh, stream_slice=next_stream_slice))
        records.extend(next_records)
        checkpoint_reader.observe(stream.state)
        assert checkpoint_reader.get_checkpoint() == expected_checkpoints[i]
        next_stream_slice = checkpoint_reader.next()
        i += 1

    assert getattr(stream, "_read_pages").call_count == 3

    expected = [
        {"film": "interstellar", "id": "a200", "parent_id": "100"},
        {"film": "oppenheimer", "id": "a201", "parent_id": "100"},
        {"film": "inception", "id": "a202", "parent_id": "100"},
        {"film": "past_lives", "id": "b200", "parent_id": "101"},
        {"film": "materialists", "id": "b201", "parent_id": "101"},
        {"film": "the_social_network", "id": "c200", "parent_id": "102"},
        {"film": "gone_girl", "id": "c201", "parent_id": "102"},
        {"film": "the_curious_case_of_benjamin_button", "id": "c202", "parent_id": "102"},
    ]

    assert records == expected


def test_substream_resumable_full_refresh_read_from_state(mocker):
    """
    Validates the default behavior of a stream that supports resumable full refresh by using read_records() which gets one
    page per invocation and emits state afterward.
    parses over
    """

    parent_records = [
        {"parent_id": "100", "name": "christopher_nolan"},
        {"parent_id": "101", "name": "celine_song"},
    ]
    parent_stream = StubParentHttpStream(records=parent_records)

    parents_to_children_records = {
        "100": [
            {"id": "a200", "parent_id": "100", "film": "interstellar"},
            {"id": "a201", "parent_id": "100", "film": "oppenheimer"},
            {"id": "a202", "parent_id": "100", "film": "inception"},
        ],
        "101": [{"id": "b200", "parent_id": "101", "film": "past_lives"}, {"id": "b201", "parent_id": "101", "film": "materialists"}],
    }
    stream = StubSubstreamResumableFullRefreshStream(parent=parent_stream, partition_id_to_child_records=parents_to_children_records)

    blank_response = {}  # Send a blank response is fine as we ignore the response in `parse_response anyway.
    mocker.patch.object(stream._http_client, "send_request", return_value=(None, blank_response))

    # Wrap all methods we're interested in testing with mocked objects to spy on their input args and verify they were what we expect
    mocker.patch.object(stream, "_read_pages", wraps=getattr(stream, "_read_pages"))

    checkpoint_reader = stream._get_checkpoint_reader(
        cursor_field=[],
        logger=logging.getLogger("airbyte"),
        sync_mode=SyncMode.full_refresh,
        stream_state={
            "states": [
                {
                    "cursor": {"__ab_full_refresh_sync_complete": True},
                    "partition": {"parent": {"name": "christopher_nolan", "parent_id": "100"}},
                },
            ]
        },
    )
    next_stream_slice = checkpoint_reader.next()
    records = []

    expected_checkpoints = [
        {
            "states": [
                {
                    "cursor": {"__ab_full_refresh_sync_complete": True},
                    "partition": {"parent": {"name": "christopher_nolan", "parent_id": "100"}},
                },
                {"cursor": {"__ab_full_refresh_sync_complete": True}, "partition": {"parent": {"name": "celine_song", "parent_id": "101"}}},
            ]
        },
    ]

    i = 0
    while next_stream_slice is not None:
        next_records = list(stream.read_records(SyncMode.full_refresh, stream_slice=next_stream_slice))
        records.extend(next_records)
        checkpoint_reader.observe(stream.state)
        assert checkpoint_reader.get_checkpoint() == expected_checkpoints[i]
        next_stream_slice = checkpoint_reader.next()
        i += 1

    assert getattr(stream, "_read_pages").call_count == 1

    expected = [
        {"film": "past_lives", "id": "b200", "parent_id": "101"},
        {"film": "materialists", "id": "b201", "parent_id": "101"},
    ]

    assert records == expected


class StubWithCursorFields(StubBasicReadHttpStream):
    def __init__(self, has_multiple_slices: bool, set_cursor_field: List[str], deduplicate_query_params: bool = False, **kwargs):
        self.has_multiple_slices = has_multiple_slices
        self._cursor_field = set_cursor_field
        super().__init__()

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return self._cursor_field


@pytest.mark.parametrize(
    "cursor_field, is_substream, expected_cursor",
    [
        pytest.param([], False, ResumableFullRefreshCursor(), id="test_stream_supports_resumable_full_refresh_cursor"),
        pytest.param(["updated_at"], False, None, id="test_incremental_stream_does_not_use_cursor"),
        pytest.param(["updated_at"], True, None, id="test_incremental_substream_does_not_use_cursor"),
        pytest.param(
            [],
            True,
            SubstreamResumableFullRefreshCursor(),
            id="test_full_refresh_substream_automatically_applies_substream_resumable_full_refresh_cursor",
        ),
    ],
)
def test_get_cursor(cursor_field, is_substream, expected_cursor):
    stream = StubWithCursorFields(set_cursor_field=cursor_field, has_multiple_slices=is_substream)
    actual_cursor = stream.get_cursor()

    assert actual_cursor == expected_cursor
