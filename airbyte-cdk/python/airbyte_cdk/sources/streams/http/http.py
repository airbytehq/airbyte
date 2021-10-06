#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import Stream

from .auth.core import HttpAuthenticator, NoAuth
from .exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from .rate_limiting import default_backoff_handler, user_defined_backoff_handler

# list of all possible HTTP methods which can be used for sending of request bodies
BODY_REQUEST_METHODS = ("POST", "PUT", "PATCH")


class HttpStream(Stream, ABC):
    """
    Base abstract class for an Airbyte Stream using the HTTP protocol. Basic building block for users building an Airbyte source for a HTTP API.
    """

    source_defined_cursor = True  # Most HTTP streams use a source defined cursor (i.e: the user can't configure it like on a SQL table)

    def __init__(self, authenticator: HttpAuthenticator = NoAuth()):
        self._authenticator = authenticator
        self._session = requests.Session()

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
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        """
        Parses the raw response object into a list of records.
        By default, this returns an iterable containing the input. Override to parse differently.
        :param response:
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

        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return None

    def _create_prepared_request(
        self, path: str, headers: Mapping = None, params: Mapping = None, json: Any = None, data: Any = None
    ) -> requests.PreparedRequest:
        args = {"method": self.http_method, "url": self.url_base + path, "headers": headers, "params": params}
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

    # TODO allow configuring these parameters. If we can get this into the requests library, then we can do it without the ugly exception hacks
    #  see https://github.com/litl/backoff/pull/122
    @default_backoff_handler(max_tries=5, factor=5)
    @user_defined_backoff_handler(max_tries=5)
    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        """
        Wraps sending the request in rate limit and error handlers.

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
        response: requests.Response = self._session.send(request, **request_kwargs)
        if self.should_retry(response):
            custom_backoff_time = self.backoff_time(response)
            if custom_backoff_time:
                raise UserDefinedBackoffException(backoff=custom_backoff_time, request=request, response=response)
            else:
                raise DefaultBackoffException(request=request, response=response)
        else:
            # Raise any HTTP exceptions that happened in case there were unexpected ones
            # TODO handle ignoring errors
            response.raise_for_status()

        return response

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False

        next_page_token = None
        while not pagination_complete:
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
            yield from self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice)

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                pagination_complete = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []
