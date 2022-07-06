#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, MutableMapping, Optional, Union

import airbyte_cdk.sources.declarative.types as types
import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod, Requester
from airbyte_cdk.sources.declarative.requesters.retriers.default_retrier import DefaultRetrier
from airbyte_cdk.sources.declarative.requesters.retriers.retrier import ResponseStatus
from airbyte_cdk.sources.streams.http.requests_native_auth.token import MultipleTokenAuthenticator
from pydantic import BaseModel, validator


class HttpRequester(Requester, BaseModel):
    stream_name: str
    url_base: str
    path: str
    http_method: HttpMethod
    request_options_provider: Optional[Union[InterpolatedRequestOptionsProvider]] = None
    authenticator: Union[MultipleTokenAuthenticator]
    retrier: Optional[Union[DefaultRetrier]]
    config: types.Config

    class Config:
        arbitrary_types_allowed = True

    """
        def __init__(
                self,
                *,
                name: str,
                url_base: [str, InterpolatedString],
                path: [str, InterpolatedString],
                http_method: Union[str, HttpMethod] = HttpMethod.GET,
                request_options_provider: Optional[RequestOptionsProvider] = None,
                authenticator: HttpAuthenticator,
                retrier: Optional[Retrier] = None,
                config: Config,
        ):
            if request_options_provider is None:
                request_options_provider = InterpolatedRequestOptionsProvider(config=config)
            elif isinstance(request_options_provider, dict):
                request_options_provider = InterpolatedRequestOptionsProvider(config=config, **request_options_provider)
            self._name = name
            self._authenticator = authenticator
            if type(url_base) == str:
                url_base = InterpolatedString(string=url_base)
            self._url_base = url_base
            if type(path) == str:
                path = InterpolatedString(string=path)
            self._path: InterpolatedString = path
            if type(http_method) == str:
                http_method = HttpMethod[http_method]
            self._method = http_method
            self._request_options_provider = request_options_provider
            self._retrier = retrier or DefaultRetrier()
            self._config = config
    """

    @validator("authenticator")
    def to_auth(cls, v):
        return v

    @validator("url_base", "path")
    def to_interpolated_string(cls, v):
        if isinstance(v, str):
            return InterpolatedString(string=v)
        elif isinstance(v, InterpolatedString):
            return v
        else:
            raise TypeError(f"Expected type str or InterpolatedString for {v}. Got : {type(v)}")

    @validator("http_method")
    def to_http_method(cls, v):
        if isinstance(v, str):
            return HttpMethod[v]
        elif isinstance(v, HttpMethod):
            return v
        else:
            raise TypeError(f"Expected type str or HttpMethod for {v}. Got : {type(v)}")

    def get_authenticator(self):
        return self.authenticator

    def get_url_base(self):
        return self.url_base.eval(self.config)

    def get_path(self, *, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any], next_page_token: Mapping[str, Any]) -> str:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        path = self.path.eval(self.config, **kwargs)
        return path

    def get_method(self):
        return self.http_method

    @property
    def max_retries(self) -> Union[int, None]:
        return self.retrier.max_retries

    @property
    def retry_factor(self) -> float:
        return self.retrier.retry_factor

    # @lru_cache(maxsize=10)
    def should_retry(self, response: requests.Response) -> ResponseStatus:
        # Cache the result because the HttpStream first checks if we should retry before looking at the backoff time
        return self.retrier.should_retry(response)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return self.request_options_provider.request_params(stream_state, stream_slice, next_page_token)

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return self.request_options_provider.request_headers(stream_state, stream_slice, next_page_token)

    def request_body_data(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Union[Mapping, str]]:
        return self.request_options_provider.request_body_data(stream_state, stream_slice, next_page_token)

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping]:
        return self.request_options_provider.request_body_json(stream_state, stream_slice, next_page_token)

    def request_kwargs(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return self.request_options_provider.request_kwargs(stream_state, stream_slice, next_page_token)

    @property
    def cache_filename(self) -> str:
        # FIXME: this should be declarative
        return f"{self._name}.yml"

    @property
    def use_cache(self) -> bool:
        # FIXME: this should be declarative
        return False
