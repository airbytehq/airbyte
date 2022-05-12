#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_protocol import SyncMode
from base_python.cdk.streams.auth.core import HttpAuthenticator, NoAuth
from base_python.cdk.streams.core import Stream
from base_python.cdk.streams.exceptions import DefaultBackoffException, UserDefinedBackoffException
from base_python.cdk.streams.rate_limiting import default_backoff_handler, user_defined_backoff_handler


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
        Override if needed. See get_request_data if using POST.
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

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        """
        TODO make this possible to do for non-JSON APIs
        Override when creating POST requests to populate the body of the request with a JSON payload.
        """
        return None

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
        self, path: str, headers: Mapping = None, params: Mapping = None, json: Any = None
    ) -> requests.PreparedRequest:
        args = {"method": self.http_method, "url": self.url_base + path, "headers": headers, "params": params}

        if self.http_method.upper() == "POST":
            # TODO support non-json bodies
            args["json"] = json

        return requests.Request(**args).prepare()

    # TODO allow configuring these parameters. If we can get this into the requests library, then we can do it without the ugly exception hacks
    #  see https://github.com/litl/backoff/pull/122
    @default_backoff_handler(max_tries=5, factor=5)
    @user_defined_backoff_handler(max_tries=5)
    def _send_request(self, request: requests.PreparedRequest) -> requests.Response:
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
        response: requests.Response = self._session.send(request)
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
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        cursor_field: List[str] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        args = {"stream_state": stream_state, "stream_slice": stream_slice}
        pagination_complete = False
        while not pagination_complete:
            request = self._create_prepared_request(
                path=self.path(**args),
                headers=dict(self.request_headers(**args), **self.authenticator.get_auth_header()),
                params=self.request_params(**args),
                json=self.request_body_json(**args),
            )

            response = self._send_request(request)
            yield from self.parse_response(response, **args)

            next_page_token = self.next_page_token(response)
            if next_page_token:
                args["next_page_token"] = next_page_token
            else:
                pagination_complete = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []
