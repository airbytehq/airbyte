#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from functools import lru_cache
from typing import Any, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import RequestOptionsProvider
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod, Requester
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator, NoAuth
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class HttpRequester(Requester, JsonSchemaMixin):
    """
    Default implementation of a Requester

    Attributes:
        name (str): Name of the stream. Only used for request/response caching
        url_base (InterpolatedString): Base url to send requests to
        path (InterpolatedString): Path to send requests to
        http_method (Union[str, HttpMethod]): HTTP method to use when sending requests
        request_options_provider (Optional[RequestOptionsProvider]): request option provider defining the options to set on outgoing requests
        authenticator (HttpAuthenticator): Authenticator defining how to authenticate to the source
        error_handler (Optional[ErrorHandler]): Error handler defining how to detect and handle errors
        config (Config): The user-provided configuration as specified by the source's spec
    """

    name: str
    url_base: InterpolatedString
    path: InterpolatedString
    config: Config
    http_method: Union[str, HttpMethod] = HttpMethod.GET
    request_options_provider: Optional[RequestOptionsProvider] = None
    authenticator: HttpAuthenticator = None
    error_handler: Optional[ErrorHandler] = None
    options: InitVar[Mapping[str, Any]] = None

    def __post_init__(self, options: Mapping[str, Any]):
        if self.request_options_provider is None:
            self._request_options_provider = InterpolatedRequestOptionsProvider(config=self.config)
        elif isinstance(self.request_options_provider, dict):
            self._request_options_provider = InterpolatedRequestOptionsProvider(config=self.config, **self.request_options_provider)
        else:
            self._request_options_provider = self.request_options_provider
        self.authenticator = self.authenticator or NoAuth()
        if type(self.http_method) == str:
            self.http_method = HttpMethod[self.http_method]
        self._method = self.http_method
        self.error_handler = self.error_handler or DefaultErrorHandler()
        self._options = options or {}

    # def __init__(
    #     self,
    #     *,
    #     name: str,
    #     url_base: InterpolatedString,
    #     path: InterpolatedString,
    #     http_method: Union[str, HttpMethod] = HttpMethod.GET,
    #     request_options_provider: Optional[RequestOptionsProvider] = None,
    #     authenticator: HttpAuthenticator = None,
    #     error_handler: Optional[ErrorHandler] = None,
    #     config: Config,
    #     **options: Optional[Mapping[str, Any]],
    # ):
    #     """
    #     :param name: Name of the stream. Only used for request/response caching
    #     :param url_base: Base url to send requests to
    #     :param path: Path to send requests to
    #     :param http_method: HTTP method to use when sending requests
    #     :param request_options_provider: request option provider defining the options to set on outgoing requests
    #     :param authenticator: Authenticator defining how to authenticate to the source
    #     :param error_handler: Error handler defining how to detect and handle errors
    #     :param config: The user-provided configuration as specified by the source's spec
    #     :param options: Additional runtime parameters to be used for string interpolation
    #     """
    #     if request_options_provider is None:
    #         request_options_provider = InterpolatedRequestOptionsProvider(config=config)
    #     elif isinstance(request_options_provider, dict):
    #         request_options_provider = InterpolatedRequestOptionsProvider(config=config, **request_options_provider)
    #     self._name = name
    #     self._authenticator = authenticator or NoAuth()
    #     self._url_base = url_base
    #     self._path: InterpolatedString = path
    #     if type(http_method) == str:
    #         http_method = HttpMethod[http_method]
    #     self._method = http_method
    #     self._request_options_provider = request_options_provider
    #     self._error_handler = error_handler or DefaultErrorHandler()
    #     self._config = config
    #     self._options = options

    def get_authenticator(self):
        return self.authenticator

    def get_url_base(self):
        return self.url_base.eval(self.config)

    def get_path(
        self, *, stream_state: Optional[StreamState], stream_slice: Optional[StreamSlice], next_page_token: Optional[Mapping[str, Any]]
    ) -> str:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        path = self.path.eval(self.config, **kwargs)
        return path

    def get_method(self):
        return self._method

    # use a tiny cache to limit the memory footprint. It doesn't have to be large because we mostly
    # only care about the status of the last response received
    @lru_cache(maxsize=10)
    def should_retry(self, response: requests.Response) -> ResponseStatus:
        # Cache the result because the HttpStream first checks if we should retry before looking at the backoff time
        return self.error_handler.should_retry(response)

    def request_params(
        self, stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> MutableMapping[str, Any]:
        return self._request_options_provider.get_request_params(stream_state, stream_slice, next_page_token)

    def request_headers(
        self, stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, next_page_token: Optional[Mapping[str, Any]] = None
    ) -> Mapping[str, Any]:
        return self._request_options_provider.get_request_headers(stream_state, stream_slice, next_page_token)

    def request_body_data(
        self, stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Union[Mapping, str]]:
        return self._request_options_provider.get_request_body_data(stream_state, stream_slice, next_page_token)

    def request_body_json(
        self, stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping]:
        return self._request_options_provider.get_request_body_json(stream_state, stream_slice, next_page_token)

    def request_kwargs(
        self, stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        # todo: there are a few integrations that override the request_kwargs() method, but the use case for why kwargs over existing
        #  constructs is a little unclear. We may revisit this, but for now lets leave it out of the DSL
        return {}

    @property
    def cache_filename(self) -> str:
        # FIXME: this should be declarative
        return f"{self.name}.yml"

    @property
    def use_cache(self) -> bool:
        # FIXME: this should be declarative
        return False
