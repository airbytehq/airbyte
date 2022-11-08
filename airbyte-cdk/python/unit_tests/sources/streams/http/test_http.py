#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import Any, Iterable, Mapping, Optional
from unittest.mock import ANY, MagicMock, patch

import pytest
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator as HttpTokenAuthenticator
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class StubBasicReadHttpStream(HttpStream):
    url_base = "https://test_base_url.com"
    primary_key = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resp_counter = 1

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, **kwargs) -> str:
        return ""

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        stubResp = {"data": self.resp_counter}
        self.resp_counter += 1
        yield stubResp


def test_default_authenticator():
    stream = StubBasicReadHttpStream()
    assert isinstance(stream.authenticator, NoAuth)
    assert stream._session.auth is None


def test_requests_native_token_authenticator():
    stream = StubBasicReadHttpStream(authenticator=TokenAuthenticator("test-token"))
    assert isinstance(stream.authenticator, NoAuth)
    assert isinstance(stream._session.auth, TokenAuthenticator)


def test_http_token_authenticator():
    stream = StubBasicReadHttpStream(authenticator=HttpTokenAuthenticator("test-token"))
    assert isinstance(stream.authenticator, HttpTokenAuthenticator)
    assert stream._session.auth is None


def test_request_kwargs_used(mocker, requests_mock):
    stream = StubBasicReadHttpStream()
    request_kwargs = {"cert": None, "proxies": "google.com"}
    mocker.patch.object(stream, "request_kwargs", return_value=request_kwargs)
    send_mock = mocker.patch.object(stream._session, "send", wraps=stream._session.send)
    requests_mock.register_uri("GET", stream.url_base)

    list(stream.read_records(sync_mode=SyncMode.full_refresh))

    stream._session.send.assert_any_call(ANY, **request_kwargs)
    assert send_mock.call_count == 1


def test_stub_basic_read_http_stream_read_records(mocker):
    stream = StubBasicReadHttpStream()
    blank_response = {}  # Send a blank response is fine as we ignore the response in `parse_response anyway.
    mocker.patch.object(StubBasicReadHttpStream, "_send_request", return_value=blank_response)

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
    mocker.patch.object(StubNextPageTokenHttpStream, "_send_request", return_value=blank_response)

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

    assert expected == records


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

    stream = StubCustomBackoffHttpStreamRetries()
    req = requests.Response()
    req.status_code = HTTPStatus.TOO_MANY_REQUESTS
    send_mock = mocker.patch.object(requests.Session, "send", return_value=req)

    with pytest.raises(UserDefinedBackoffException, match="Request URL: https://test_base_url.com/, Response Code: 429") as excinfo:
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
        @property
        def max_retries(self):
            return None

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

    with pytest.raises(requests.exceptions.HTTPError):
        list(stream.read_records(SyncMode.full_refresh))


class AutoFailFalseHttpStream(StubBasicReadHttpStream):
    raise_on_http_errors = False
    max_retries = 3
    retry_factor = 0.01


def test_raise_on_http_errors_off_429(mocker):
    stream = AutoFailFalseHttpStream()
    req = requests.Response()
    req.status_code = 429

    mocker.patch.object(requests.Session, "send", return_value=req)
    with pytest.raises(DefaultBackoffException, match="Request URL: https://test_base_url.com/, Response Code: 429"):
        list(stream.read_records(SyncMode.full_refresh))


@pytest.mark.parametrize("status_code", [500, 501, 503, 504])
def test_raise_on_http_errors_off_5xx(mocker, status_code):
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
    response = stream._send_request(req, {})
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
    stream = AutoFailFalseHttpStream()
    send_mock = mocker.patch.object(requests.Session, "send", side_effect=error())

    with pytest.raises(error):
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

    assert stream_1._session != stream_2._session
    assert stream_1.cache_filename == stream_2.cache_filename


def test_parent_attribute_exist():
    parent_stream = CacheHttpStream()
    child_stream = CacheHttpSubStream(parent=parent_stream)

    assert child_stream.parent == parent_stream


def test_cache_response(mocker):
    stream = CacheHttpStream()
    mocker.patch.object(stream, "url_base", "https://google.com/")
    list(stream.read_records(sync_mode=SyncMode.full_refresh))

    with open(stream.cache_filename, "rb") as f:
        assert f.read()


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

    assert requests_mock.call_count == 0
    assert parent_stream._session.cache.response_count() == 0

    for _slice in parent_stream.stream_slices():
        list(parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=_slice))

    assert requests_mock.call_count == 2
    assert parent_stream._session.cache.response_count() == 2

    child_stream = CacheHttpSubStream(parent=parent_stream)

    for _slice in child_stream.stream_slices(sync_mode=SyncMode.full_refresh):
        pass

    assert requests_mock.call_count == 2
    assert parent_stream._session.cache.response_count() == 2
    assert parent_stream._session.cache.has_url("https://google.com/")
    assert parent_stream._session.cache.has_url("https://google.com/search")


class AutoFailTrueHttpStream(StubBasicReadHttpStream):
    raise_on_http_errors = True


@pytest.mark.parametrize("status_code", range(400, 600))
def test_send_raise_on_http_errors_logs(mocker, status_code):
    mocker.patch.object(AutoFailTrueHttpStream, "logger")
    mocker.patch.object(AutoFailTrueHttpStream, "should_retry", mocker.Mock(return_value=False))
    stream = AutoFailTrueHttpStream()
    req = requests.PreparedRequest()
    res = requests.Response()
    res.status_code = status_code
    mocker.patch.object(requests.Session, "send", return_value=res)
    with pytest.raises(requests.exceptions.HTTPError):
        response = stream._send_request(req, {})
        stream.logger.error.assert_called_with(response.text)
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

    http_err_msg = stream.get_error_display_message(requests.HTTPError())
    assert http_err_msg == "my custom message"
