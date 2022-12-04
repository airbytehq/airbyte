#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
from dataclasses import InitVar, dataclass
from functools import lru_cache
from typing import Any, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator, NoAuth
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod, Requester
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class HttpRequester(Requester, JsonSchemaMixin):
    """
    Default implementation of a Requester

    Attributes:
        name (str): Name of the stream. Only used for request/response caching
        url_base (Union[InterpolatedString, str]): Base url to send requests to
        path (Union[InterpolatedString, str]): Path to send requests to
        http_method (Union[str, HttpMethod]): HTTP method to use when sending requests
        request_options_provider (Optional[InterpolatedRequestOptionsProvider]): request option provider defining the options to set on outgoing requests
        authenticator (DeclarativeAuthenticator): Authenticator defining how to authenticate to the source
        error_handler (Optional[ErrorHandler]): Error handler defining how to detect and handle errors
        config (Config): The user-provided configuration as specified by the source's spec
    """

    name: str
    url_base: Union[InterpolatedString, str]
    path: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]
    http_method: Union[str, HttpMethod] = HttpMethod.GET
    request_options_provider: Optional[InterpolatedRequestOptionsProvider] = None
    authenticator: DeclarativeAuthenticator = None
    error_handler: Optional[ErrorHandler] = None

    def __post_init__(self, options: Mapping[str, Any]):
        self.url_base = InterpolatedString.create(self.url_base, options=options)
        self.path = InterpolatedString.create(self.path, options=options)
        if self.request_options_provider is None:
            self._request_options_provider = InterpolatedRequestOptionsProvider(config=self.config, options=options)
        elif isinstance(self.request_options_provider, dict):
            self._request_options_provider = InterpolatedRequestOptionsProvider(config=self.config, **self.request_options_provider)
        else:
            self._request_options_provider = self.request_options_provider
        self.authenticator = self.authenticator or NoAuth(options)
        if type(self.http_method) == str:
            self.http_method = HttpMethod[self.http_method]
        self._method = self.http_method
        self.error_handler = self.error_handler or DefaultErrorHandler(options=options, config=self.config)
        self._options = options

    # We are using an LRU cache in should_retry() method which requires all incoming arguments (including self) to be hashable.
    # Dataclasses by default are not hashable, so we need to define __hash__(). Alternatively, we can set @dataclass(frozen=True),
    # but this has a cascading effect where all dataclass fields must also be set to frozen.
    def __hash__(self):
        return hash(tuple(self.__dict__))

    def get_authenticator(self):
        return self.authenticator

    def get_url_base(self):
        return os.path.join(self.url_base.eval(self.config), "")

    def get_path(
        self, *, stream_state: Optional[StreamState], stream_slice: Optional[StreamSlice], next_page_token: Optional[Mapping[str, Any]]
    ) -> str:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        path = self.path.eval(self.config, **kwargs)
        return path.strip("/")

    def get_method(self):
        return self._method

    # use a tiny cache to limit the memory footprint. It doesn't have to be large because we mostly
    # only care about the status of the last response received
    @lru_cache(maxsize=10)
    def interpret_response_status(self, response: requests.Response) -> ResponseStatus:
        # Cache the result because the HttpStream first checks if we should retry before looking at the backoff time
        return self.error_handler.interpret_response(response)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return self._request_options_provider.get_request_params(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._request_options_provider.get_request_headers(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Union[Mapping, str]]:
        return self._request_options_provider.get_request_body_data(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        return self._request_options_provider.get_request_body_json(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )

    def request_kwargs(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
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
