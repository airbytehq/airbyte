#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
import os
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from urllib.parse import urljoin

import requests
import requests_cache
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import Stream, StreamData
from requests.auth import AuthBase
from requests_cache.session import CachedSession

from .auth.core import HttpAuthenticator, NoAuth
from .exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from .rate_limiting import default_backoff_handler, user_defined_backoff_handler

# list of all possible HTTP methods which can be used for sending of request bodies
BODY_REQUEST_METHODS = ("GET", "POST", "PUT", "PATCH")


class HttpStream(Stream, ABC):
    """
    Base abstract class for an Airbyte Stream using the HTTP protocol. Basic building block for users building an Airbyte source for a HTTP API.
    """

    source_defined_cursor = True  # Most HTTP streams use a source defined cursor (i.e: the user can't configure it like on a SQL table)
    page_size: Optional[int] = None  # Use this variable to define page size for API http requests with pagination support

    # TODO: remove legacy HttpAuthenticator authenticator references
    def __init__(self, authenticator: Union[AuthBase, HttpAuthenticator] = None):
        if self.use_cache:
            self._session = self.request_cache()
        else:
            self._session = requests.Session()

        self._authenticator: HttpAuthenticator = NoAuth()
        if isinstance(authenticator, AuthBase):
            self._session.auth = authenticator
        elif authenticator:
            self._authenticator = authenticator

    @property
    def cache_filename(self):
        """
        Override if needed. Return the name of cache file
        """
        return f"{self.name}.sqlite"

    @property
    def use_cache(self):
        """
        Override if needed. If True, all records will be cached.
        """
        return False

    def request_cache(self) -> CachedSession:
        self.clear_cache()
        return requests_cache.CachedSession(self.cache_filename)

    def clear_cache(self):
        """
        remove cache file only once
        """
        STREAM_CACHE_FILES = globals().setdefault("STREAM_CACHE_FILES", set())
        if self.cache_filename not in STREAM_CACHE_FILES:
            with suppress(FileNotFoundError):
                os.remove(self.cache_filename)
            STREAM_CACHE_FILES.add(self.cache_filename)

    @property
    @abstractmethod
    def url_base(self) -> str:
        """
        :return: URL base for the  API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "https://myapi.com/v1/"
        """

    @property
    def http_method(self) -> str:
        """
        Override if needed. See get_request_data/get_request_json if using POST/PUT/PATCH.
        """
        return "GET"

    @property
    def raise_on_http_errors(self) -> bool:
        """
        Override if needed. If set to False, allows opting-out of raising HTTP code exception.
        """
        return True

    @property
    def max_retries(self) -> Union[int, None]:
        """
        Override if needed. Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """
        return 5

    @property
    def retry_factor(self) -> float:
        """
        Override if needed. Specifies factor for backoff policy.
        """
        return 5

    @property
    def authenticator(self) -> HttpAuthenticator:
        return self._authenticator

    @abstractmethod
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Override this method to define a pagination strategy.

        The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.

        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """

    @abstractmethod
    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        """
        Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"
        """

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define the query parameters that should be set on an outgoing HTTP request given the inputs.

        E.g: you might want to define query parameters for paging if next_page_token is not None.
        """
        return {}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return {}

    def request_body_data(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        """
        Override when creating POST/PUT/PATCH requests to populate the body of the request with a non-JSON payload.

        If returns a ready text that it will be sent as is.
        If returns a dict that it will be converted to a urlencoded form.
        E.g. {"key1": "value1", "key2": "value2"} => "key1=value1&key2=value2"

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """
        return None

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        """
        Override when creating POST/PUT/PATCH requests to populate the body of the request with a JSON payload.

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """
        return None

    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        """
        Override to return a mapping of keyword arguments to be used when creating the HTTP request.
        Any option listed in https://docs.python-requests.org/en/latest/api/#requests.adapters.BaseAdapter.send for can be returned from
        this method. Note that these options do not conflict with request-level options such as headers, request params, etc..
        """
        return {}

    @abstractmethod
    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        """
        Parses the raw response object into a list of records.
        By default, this returns an iterable containing the input. Override to parse differently.
        :param response:
        :param stream_state:
        :param stream_slice:
        :param next_page_token:
        :return: An iterable containing the parsed response
        """

    # TODO move all the retry logic to a functor/decorator which is input as an init parameter
    def should_retry(self, response: requests.Response) -> bool:
        """
        Override to set different conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors

        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        """
        return response.status_code == 429 or 500 <= response.status_code < 600

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return None

    def error_message(self, response: requests.Response) -> str:
        """
        Override this method to specify a custom error message which can incorporate the HTTP response received

        :param response: The incoming HTTP response from the partner API
        :return:
        """
        return ""

    def _create_prepared_request(
        self,
        path: str,
        headers: Mapping = None,
        params: Mapping = None,
        json: Any = None,
        data: Any = None,
    ) -> requests.PreparedRequest:
        args = {"method": self.http_method, "url": urljoin(self.url_base, path), "headers": headers, "params": params}
        if self.http_method.upper() in BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data

        return self._session.prepare_request(requests.Request(**args))

    def _send(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        """
        Wraps sending the request in rate limit and error handlers.
        Please note that error handling for HTTP status codes will be ignored if raise_on_http_errors is set to False

        This method handles two types of exceptions:
            1. Expected transient exceptions e.g: 429 status code.
            2. Unexpected transient exceptions e.g: timeout.

        To trigger a backoff, we raise an exception that is handled by the backoff decorator. If an exception is not handled by the decorator will
        fail the sync.

        For expected transient exceptions, backoff time is determined by the type of exception raised:
            1. CustomBackoffException uses the user-provided backoff value
            2. DefaultBackoffException falls back on the decorator's default behavior e.g: exponential backoff

        Unexpected transient exceptions use the default backoff parameters.
        Unexpected persistent exceptions are not handled and will cause the sync to fail.
        """
        self.logger.debug(
            "Making outbound API request", extra={"headers": request.headers, "url": request.url, "request_body": request.body}
        )
        response: requests.Response = self._session.send(request, **request_kwargs)

        # Evaluation of response.text can be heavy, for example, if streaming a large response
        # Do it only in debug mode
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                "Receiving response", extra={"headers": response.headers, "status": response.status_code, "body": response.text}
            )
        if self.should_retry(response):
            custom_backoff_time = self.backoff_time(response)
            error_message = self.error_message(response)
            if custom_backoff_time:
                raise UserDefinedBackoffException(
                    backoff=custom_backoff_time, request=request, response=response, error_message=error_message
                )
            else:
                raise DefaultBackoffException(request=request, response=response, error_message=error_message)
        elif self.raise_on_http_errors:
            # Raise any HTTP exceptions that happened in case there were unexpected ones
            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                self.logger.error(response.text)
                raise exc
        return response

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        """
        Creates backoff wrappers which are responsible for retry logic
        """

        """
        Backoff package has max_tries parameter that means total number of
        tries before giving up, so if this number is 0 no calls expected to be done.
        But for this class we call it max_REtries assuming there would be at
        least one attempt and some retry attempts, to comply this logic we add
        1 to expected retries attempts.
        """
        max_tries = self.max_retries
        """
        According to backoff max_tries docstring:
            max_tries: The maximum number of attempts to make before giving
                up ...The default value of None means there is no limit to
                the number of tries.
        This implies that if max_tries is explicitly set to None there is no
        limit to retry attempts, otherwise it is limited number of tries. But
        this is not true for current version of backoff packages (1.8.0). Setting
        max_tries to 0 or negative number would result in endless retry attempts.
        Add this condition to avoid an endless loop if it hasn't been set
        explicitly (i.e. max_retries is not None).
        """
        if max_tries is not None:
            max_tries = max(0, max_tries) + 1

        user_backoff_handler = user_defined_backoff_handler(max_tries=max_tries)(self._send)
        backoff_handler = default_backoff_handler(max_tries=max_tries, factor=self.retry_factor)
        return backoff_handler(user_backoff_handler)(request, request_kwargs)

    @classmethod
    def parse_response_error_message(cls, response: requests.Response) -> Optional[str]:
        """
        Parses the raw response object from a failed request into a user-friendly error message.
        By default, this method tries to grab the error message from JSON responses by following common API patterns. Override to parse differently.

        :param response:
        :return: A user-friendly message that indicates the cause of the error
        """

        # default logic to grab error from common fields
        def _try_get_error(value):
            if isinstance(value, str):
                return value
            elif isinstance(value, list):
                return ", ".join(_try_get_error(v) for v in value)
            elif isinstance(value, dict):
                new_value = (
                    value.get("message")
                    or value.get("messages")
                    or value.get("error")
                    or value.get("errors")
                    or value.get("failures")
                    or value.get("failure")
                    or value.get("detail")
                )
                return _try_get_error(new_value)
            return None

        try:
            body = response.json()
            return _try_get_error(body)
        except requests.exceptions.JSONDecodeError:
            return None

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.

        The default implementation of this method only handles HTTPErrors by passing the response to self.parse_response_error_message().
        The method should be overriden as needed to handle any additional exception types.

        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error
        """
        if isinstance(exception, requests.HTTPError):
            return self.parse_response_error_message(exception.response)
        return None

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[StreamData]:
        yield from self._read_pages(
            lambda req, res, state, _slice: self.parse_response(res, stream_slice=_slice, stream_state=state), stream_slice, stream_state
        )

    def _read_pages(
        self,
        records_generator_fn: Callable[
            [requests.PreparedRequest, requests.Response, Mapping[str, Any], Mapping[str, Any]], Iterable[StreamData]
        ],
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[StreamData]:
        stream_state = stream_state or {}
        pagination_complete = False
        next_page_token = None
        while not pagination_complete:
            request, response = self._fetch_next_page(stream_slice, stream_state, next_page_token)
            yield from records_generator_fn(request, response, stream_state, stream_slice)

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                pagination_complete = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []

    def _fetch_next_page(
        self, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        request = self._create_prepared_request(
            path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
            params=self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
        )
        request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        response = self._send_request(request, request_kwargs)
        return request, response


class HttpSubStream(HttpStream, ABC):
    def __init__(self, parent: HttpStream, **kwargs):
        """
        :param parent: should be the instance of HttpStream class
        """
        super().__init__(**kwargs)
        self.parent = parent

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            # iterate over all parent records with current stream_slice
            for record in parent_records:
                yield {"parent": record}
