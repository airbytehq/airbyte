#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Mapping, MutableMapping, Optional, Union

import requests
from requests.auth import AuthBase


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"


class Requester(ABC):
    @abstractmethod
    def get_authenticator(self) -> AuthBase:
        """
        Specifies the authenticator to use when submitting requests
        """
        pass

    @abstractmethod
    def get_url_base(self) -> str:
        """
        :return: URL base for the  API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "https://myapi.com/v1/"
        """

    @abstractmethod
    def get_path(self, *, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any], next_page_token: Mapping[str, Any]) -> str:
        """
        Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"
        """

    @abstractmethod
    def get_method(self) -> HttpMethod:
        """
        Specifies the HTTP method to use
        """

    @abstractmethod
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """
        Specifies the query parameters that should be set on an outgoing HTTP request given the inputs.

        E.g: you might want to define query parameters for paging if next_page_token is not None.
        """

    @property
    @abstractmethod
    def raise_on_http_errors(self) -> bool:
        """
        If set to False, allows opting-out of raising HTTP code exception.
        """

    @property
    @abstractmethod
    def max_retries(self) -> Union[int, None]:
        """
        Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """

    @property
    @abstractmethod
    def retry_factor(self) -> float:
        """
        Specifies factor for backoff policy.
        """

    @abstractmethod
    def should_retry(self, response: requests.Response) -> bool:
        """
        Specifies conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors

        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        """

    @abstractmethod
    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """

    @abstractmethod
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """

    @abstractmethod
    def request_body_data(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        """
        Specifies how to populate the body of the request with a non-JSON payload.

        If returns a ready text that it will be sent as is.
        If returns a dict that it will be converted to a urlencoded form.
        E.g. {"key1": "value1", "key2": "value2"} => "key1=value1&key2=value2"

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """

    @abstractmethod
    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        """
        Specifies how to populate the body of the request with a JSON payload.

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """

    @abstractmethod
    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        """
        Returns a mapping of keyword arguments to be used when creating the HTTP request.
        Any option listed in https://docs.python-requests.org/en/latest/api/#requests.adapters.BaseAdapter.send for can be returned from
        this method. Note that these options do not conflict with request-level options such as headers, request params, etc..
        """

    @property
    @abstractmethod
    def cache_filename(self) -> str:
        """
        Return the name of cache file
        """

    @property
    @abstractmethod
    def use_cache(self) -> bool:
        """
        If True, all records will be cached.
        """
