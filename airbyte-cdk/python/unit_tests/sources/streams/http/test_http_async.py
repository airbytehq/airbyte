#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import asyncio
import json
from http import HTTPStatus
from typing import Any, Iterable, Mapping, Optional
from unittest.mock import ANY, MagicMock, patch
from yarl import URL

import aiohttp
import pytest
import requests
from aioresponses import CallbackResult, aioresponses
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import NoAuth
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator as HttpTokenAuthenticator
from airbyte_cdk.sources.streams.http.http_async import AsyncHttpStream, AsyncHttpSubStream
from airbyte_cdk.sources.streams.http.exceptions_async import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class StubBasicReadHttpStream(AsyncHttpStream):
    url_base = "https://test_base_url.com"
    primary_key = ""

    def __init__(self, deduplicate_query_params: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.resp_counter = 1
        self._deduplicate_query_params = deduplicate_query_params

    async def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, **kwargs) -> str:
        return ""

    async def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        stubResp = {"data": self.resp_counter}
        self.resp_counter += 1
        yield stubResp

    def must_deduplicate_query_params(self) -> bool:
        return self._deduplicate_query_params


def test_default_authenticator():
    stream = StubBasicReadHttpStream()
    assert isinstance(stream.authenticator, NoAuth)


def test_http_token_authenticator():
    stream = StubBasicReadHttpStream(authenticator=HttpTokenAuthenticator("test-token"))
    assert isinstance(stream.authenticator, HttpTokenAuthenticator)


def test_request_kwargs_used(mocker):
    loop = asyncio.get_event_loop()
    stream = StubBasicReadHttpStream()
    loop.run_until_complete(stream.ensure_session())

    request_kwargs = {"chunked": True, "compress": True}
    mocker.patch.object(stream, "request_kwargs", return_value=request_kwargs)

    with aioresponses() as m:
        m.get(stream.url_base, status=200)
        loop.run_until_complete(read_records(stream))

        m.assert_any_call(stream.url_base, "GET", **request_kwargs)
        m.assert_called_once()


async def read_records(stream, sync_mode=SyncMode.full_refresh, stream_slice=None):
    records = []
    async for record in stream.read_records(sync_mode=sync_mode, stream_slice=stream_slice):
        records.append(record)
    return records


def test_stub_basic_read_http_stream_read_records(mocker):
    loop = asyncio.get_event_loop()
    stream = StubBasicReadHttpStream()
    blank_response = {}  # Send a blank response is fine as we ignore the response in `parse_response anyway.
    mocker.patch.object(StubBasicReadHttpStream, "_send_request", return_value=blank_response)

    records = loop.run_until_complete(read_records(stream))

    assert [{"data": 1}] == records


class StubNextPageTokenHttpStream(StubBasicReadHttpStream):
    current_page = 0

    def __init__(self, pages: int = 5):
        super().__init__()
        self._pages = pages

    async def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
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

    loop = asyncio.get_event_loop()
    records = loop.run_until_complete(read_records(stream))

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


def test_stub_bad_url_http_stream_read_records():
    stream = StubBadUrlHttpStream()
    loop = asyncio.get_event_loop()
    with pytest.raises(aiohttp.client_exceptions.InvalidURL):
        loop.run_until_complete(read_records(stream))


class StubCustomBackoffHttpStream(StubBasicReadHttpStream):
    def backoff_time(self, response: requests.Response) -> Optional[float]:
        return 0.5


def test_stub_custom_backoff_http_stream(mocker):
    mocker.patch("time.sleep", lambda x: None)
    stream = StubCustomBackoffHttpStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())
    call_counter = 0

    def request_callback(*args, **kwargs):
        nonlocal call_counter
        call_counter += 1

    with aioresponses() as m:
        m.get(stream.url_base, status=429, repeat=True, callback=request_callback)

        with pytest.raises(UserDefinedBackoffException):
            loop.run_until_complete(read_records(stream))

    assert call_counter == stream.max_retries + 1


@pytest.mark.parametrize("retries", [-20, -1, 0, 1, 2, 10])
def test_stub_custom_backoff_http_stream_retries(mocker, retries):
    mocker.patch("time.sleep", lambda x: None)

    class StubCustomBackoffHttpStreamRetries(StubCustomBackoffHttpStream):
        @property
        def max_retries(self):
            return retries

    def request_callback(*args, **kwargs):
        nonlocal call_counter
        call_counter += 1

    stream = StubCustomBackoffHttpStreamRetries()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())
    call_counter = 0

    with aioresponses() as m:
        m.get(stream.url_base, status=429, repeat=True, callback=request_callback)

        with pytest.raises(UserDefinedBackoffException) as excinfo:
            loop.run_until_complete(read_records(stream))
            assert isinstance(excinfo.value.request, aiohttp.ClientRequest)
            assert isinstance(excinfo.value.response, aiohttp.ClientResponse)

        if retries <= 0:
            m.assert_called_once()
        else:
            assert call_counter == stream.max_retries + 1


def test_stub_custom_backoff_http_stream_endless_retries(mocker):
    mocker.patch("time.sleep", lambda x: None)

    class StubCustomBackoffHttpStreamRetries(StubCustomBackoffHttpStream):
        @property
        def max_retries(self):
            return None

    stream = StubCustomBackoffHttpStreamRetries()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())
    infinite_number = 20
    call_counter = 0

    with aioresponses() as m:
        def request_callback(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1
            if call_counter > infinite_number:
                # Simulate a different response or a break in the pattern
                # to stop the infinite retries
                raise RuntimeError("End of retries")

        m.get(stream.url_base, status=HTTPStatus.TOO_MANY_REQUESTS, repeat=True, callback=request_callback)

        # Expecting mock object to raise a RuntimeError when the end of side_effect list parameter reached.
        with pytest.raises(RuntimeError):
            loop.run_until_complete(read_records(stream))

    assert call_counter == infinite_number + 1


@pytest.mark.parametrize("http_code", [400, 401, 403])
def test_4xx_error_codes_http_stream(http_code):
    stream = StubCustomBackoffHttpStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())

    with aioresponses() as m:
        m.get(stream.url_base, status=http_code, repeat=True)

        with pytest.raises(aiohttp.ClientResponseError):
            loop.run_until_complete(read_records(stream))


class AutoFailFalseHttpStream(StubBasicReadHttpStream):
    raise_on_http_errors = False
    max_retries = 3
    retry_factor = 0.01


def test_raise_on_http_errors_off_429():
    stream = AutoFailFalseHttpStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())

    with aioresponses() as m:
        m.get(stream.url_base, status=429, repeat=True)
        with pytest.raises(DefaultBackoffException):
            loop.run_until_complete(read_records(stream))


@pytest.mark.parametrize("status_code", [500, 501, 503, 504])
def test_raise_on_http_errors_off_5xx(status_code):
    stream = AutoFailFalseHttpStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())
    call_counter = 0

    def request_callback(*args, **kwargs):
        nonlocal call_counter
        call_counter += 1

    with aioresponses() as m:
        m.get(stream.url_base, status=status_code, repeat=True, callback=request_callback)
        with pytest.raises(DefaultBackoffException):
            loop.run_until_complete(read_records(stream))

    assert call_counter == stream.max_retries + 1


@pytest.mark.parametrize("status_code", [400, 401, 402, 403, 416])
def test_raise_on_http_errors_off_non_retryable_4xx(status_code):
    stream = AutoFailFalseHttpStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())

    with aioresponses() as m:
        m.get(stream.url_base, status=status_code, repeat=True)
        response = loop.run_until_complete(stream._send_request(aiohttp.ClientRequest("GET", URL(stream.url_base)), {}))

    assert response.status == status_code


@pytest.mark.parametrize(
    "error",
    (
        aiohttp.ServerDisconnectedError,
        aiohttp.ServerConnectionError,
        aiohttp.ServerTimeoutError,
    ),
)
def test_raise_on_http_errors(error):
    stream = AutoFailFalseHttpStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())
    call_counter = 0

    def request_callback(*args, **kwargs):
        nonlocal call_counter
        call_counter += 1

    with aioresponses() as m:
        m.get(stream.url_base, repeat=True, callback=request_callback, exception=error())

        with pytest.raises(error):
            loop.run_until_complete(read_records(stream))

    assert call_counter == stream.max_retries + 1


class PostHttpStream(StubBasicReadHttpStream):
    http_method = "POST"

    async def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """Returns response data as is"""
        yield response.json()


class TestRequestBody:
    """Suite of different tests for request bodies"""

    json_body = {"key": "value"}
    data_body = "key:value"
    form_body = {"key1": "value1", "key2": 1234}
    urlencoded_form_body = "key1=value1&key2=1234"

    def request2response(self, **kwargs):
        """Callback function to handle request and return mock response."""
        body = kwargs.get("data")
        headers = kwargs.get("headers", {})
        return {
            "body": json.dumps(body) if isinstance(body, dict) else body,
            "content_type": headers.get("Content-Type")
        }

    def test_json_body(self, mocker):
        stream = PostHttpStream()
        mocker.patch.object(stream, "request_body_json", return_value=self.json_body)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(stream.ensure_session())

        with aioresponses() as m:
            m.post(stream.url_base, payload=self.request2response(data=self.json_body, headers={"Content-Type": "application/json"}))

            response = []
            for r in loop.run_until_complete(read_records(stream)):
                response.append(loop.run_until_complete(r))

        assert response[0]["content_type"] == "application/json"
        assert json.loads(response[0]["body"]) == self.json_body

    def test_text_body(self, mocker):
        stream = PostHttpStream()
        mocker.patch.object(stream, "request_body_data", return_value=self.data_body)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(stream.ensure_session())

        with aioresponses() as m:
            m.post(stream.url_base, payload=self.request2response(data=self.data_body))

            response = []
            for r in loop.run_until_complete(read_records(stream)):
                response.append(loop.run_until_complete(r))

        assert response[0]["content_type"] is None
        assert response[0]["body"] == self.data_body

    def test_form_body(self, mocker):
        raise NotImplementedError("This is not supported for the async flow yet.")

    def test_text_json_body(self, mocker):
        """checks a exception if both functions were overridden"""
        stream = PostHttpStream()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(stream.ensure_session())

        mocker.patch.object(stream, "request_body_data", return_value=self.data_body)
        mocker.patch.object(stream, "request_body_json", return_value=self.json_body)

        with aioresponses() as m:
            m.post(stream.url_base, payload=self.request2response(data=self.data_body))
            with pytest.raises(RequestBodyException):
                loop.run_until_complete(read_records(stream))

    def test_body_for_all_methods(self, mocker, requests_mock):
        """Stream must send a body for GET/POST/PATCH/PUT methods only"""
        stream = PostHttpStream()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(stream.ensure_session())

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

            with aioresponses() as m:
                if method == "POST":
                    request = m.post
                elif method == "PUT":
                    request = m.put
                elif method == "PATCH":
                    request = m.patch
                elif method == "GET":
                    request = m.get
                elif method == "DELETE":
                    request = m.delete
                elif method == "OPTIONS":
                    request = m.options

                request(stream.url_base, payload=self.request2response(data=self.data_body))

                response = []
                for r in loop.run_until_complete(read_records(stream)):
                    response.append(loop.run_until_complete(r))

            # The requests library flow strips the body where `with_body` is False, but
            # aiohttp does not.
            assert response[0]["body"] == self.data_body


class CacheHttpStream(StubBasicReadHttpStream):
    use_cache = True


class CacheHttpSubStream(AsyncHttpSubStream):
    url_base = "https://example.com"
    primary_key = ""

    def __init__(self, parent):
        super().__init__(parent=parent)

    async def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield None

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
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream_1.ensure_session())
    loop.run_until_complete(stream_2.ensure_session())

    assert stream_1._session != stream_2._session
    assert stream_1.cache_filename == stream_2.cache_filename


def test_parent_attribute_exist():
    parent_stream = CacheHttpStream()
    child_stream = CacheHttpSubStream(parent=parent_stream)

    assert child_stream.parent == parent_stream


def test_that_response_was_cached(mocker):
    stream = CacheHttpStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())
    loop.run_until_complete(stream.clear_cache())

    mocker.patch.object(stream, "url_base", "https://google.com/")

    with aioresponses() as m1:
        m1.get(stream.url_base)
        records = loop.run_until_complete(read_records(stream))
        m1.assert_called_once()

    with aioresponses() as m2:
        m2.get(stream.url_base)
        new_records = loop.run_until_complete(read_records(stream))
        m2.assert_not_called()

    assert len(records) == len(new_records)


class CacheHttpStreamWithSlices(CacheHttpStream):
    paths = ["", "search"]

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f'{stream_slice["path"]}' if stream_slice else ""

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for path in self.paths:
            yield {"path": path}

    async def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {"value": len(await response.text())}


@patch("airbyte_cdk.sources.streams.core.logging", MagicMock())
def test_using_cache(mocker):
    raise NotImplementedError("giving up for now")
    parent_stream = CacheHttpStreamWithSlices()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parent_stream.ensure_session())
    loop.run_until_complete(parent_stream.clear_cache())

    mocker.patch.object(parent_stream, "url_base", "https://google.com/")

    call_counter = 0
    def request_callback(*args, **kwargs):
        nonlocal call_counter
        call_counter += 1

    with aioresponses() as m:

        # assert len(parent_stream._session.cache.responses) == 0

        slices = list(parent_stream.stream_slices())
        m.get(parent_stream.url_base, repeat=True, callback=request_callback, payload=slices[0])
        m.get(parent_stream.url_base, repeat=True, callback=request_callback, payload=slices[1])

        assert call_counter == 0


        r1 = loop.run_until_complete(read_records(parent_stream, stream_slice=slices[0]))
        r2 = loop.run_until_complete(read_records(parent_stream, stream_slice=slices[1]))

        assert call_counter == 2
        # assert len(parent_stream._session.cache.responses) == 2
        #
        # child_stream = CacheHttpSubStream(parent=parent_stream)
        #
        # for _slice in child_stream.stream_slices(sync_mode=SyncMode.full_refresh):
        #     pass
        #
        # assert call_counter == 2
        # assert len(parent_stream._session.cache.responses) == 2
        # assert parent_stream._session.cache.contains(url="https://google.com/")
        # assert parent_stream._session.cache.contains(url="https://google.com/search")
        #


class AutoFailTrueHttpStream(StubBasicReadHttpStream):
    raise_on_http_errors = True


@pytest.mark.parametrize("status_code", range(400, 600))
def test_send_raise_on_http_errors_logs(mocker, status_code):
    mocker.patch.object(AutoFailTrueHttpStream, "logger")
    mocker.patch.object(AutoFailTrueHttpStream, "should_retry", mocker.Mock(return_value=False))

    stream = AutoFailTrueHttpStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())

    req = aiohttp.ClientRequest("GET", URL(stream.url_base))

    with aioresponses() as m:
        m.get(stream.url_base, status=status_code, repeat=True, payload="text")

        with pytest.raises(aiohttp.ClientError):
            response = loop.run_until_complete(stream._send_request(req, {}))
            stream.logger.error.assert_called_with("text")
            assert response.status == status_code


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
    loop = asyncio.get_event_loop()
    response = MagicMock()
    response.json.return_value = _get_response(api_response)

    message = loop.run_until_complete(stream.parse_response_error_message(response))
    assert message == expected_message


async def _get_response(response):
    return response


def test_default_parse_response_error_message_not_json():
    stream = StubBasicReadHttpStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())

    req = aiohttp.ClientRequest("GET", URL("mock://test.com/not_json"))

    def callback(url, **kwargs):
        return CallbackResult(body="this is not json")

    with aioresponses() as m:
        m.get("mock://test.com/not_json", callback=callback)
        response = loop.run_until_complete(stream._send_request(req, {}))
        message = loop.run_until_complete(stream.parse_response_error_message(response))
    assert message is None


def test_default_get_error_display_message_handles_http_error(mocker):
    stream = StubBasicReadHttpStream()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())

    mocker.patch.object(stream, "parse_response_error_message", return_value="my custom message")

    non_http_err_msg = loop.run_until_complete(stream.get_error_display_message(RuntimeError("not me")))
    assert non_http_err_msg is None

    req = aiohttp.ClientRequest("GET", URL("mock://test.com/not_json"))

    with aioresponses() as m:
        m.get("mock://test.com/not_json")
        response = loop.run_until_complete(stream._send_request(req, {}))
        http_exception = aiohttp.ClientResponseError(request_info=None, history=None, message=response)

    http_err_msg = loop.run_until_complete(stream.get_error_display_message(http_exception))
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
    actual_url = AsyncHttpStream._join_url(base_url, path)
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
            stream._create_prepared_request(path=path, params=params)
    else:
        prepared_request = stream._create_prepared_request(path=path, params=params)
        assert str(prepared_request.url) == expected_url


def test_connection_pool():
    stream = StubBasicReadHttpStream(authenticator=HttpTokenAuthenticator("test-token"))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream.ensure_session())
    assert stream._session.connector.limit == 20
