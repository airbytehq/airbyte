#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from enum import Enum
from typing import Any, Mapping, MutableMapping

from airbyte_cdk.sources.cac.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.cac.requesters.request_params.request_parameters_provider import RequestParameterProvider
from airbyte_cdk.sources.cac.requesters.requester import Requester


class HttpMethod(Enum):
    GET = "GET"


class HttpRequester(Requester):
    def __init__(
        self,
        url_base: str = None,
        path: [str, InterpolatedString] = None,
        http_method: HttpMethod = None,
        request_parameters_provider: RequestParameterProvider = None,
        authenticator=None,
        config=None,
        kwargs=None,
    ):
        self._vars = vars
        self._authenticator = authenticator or kwargs.get("authenticator")
        self._url_base = url_base or kwargs.get("url_base")
        if type(path) == str:
            path = InterpolatedString(path, path)
        self._path: InterpolatedString = path or kwargs.get("path")
        self._method = http_method or kwargs.get("http_method")
        self._request_parameters_provider = request_parameters_provider or kwargs.get("request_parameters_provider")
        self._config = config or kwargs.get("config")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return self._request_parameters_provider.request_params(stream_state, stream_slice, next_page_token)

    def get_authenticator(self):
        return self._authenticator

    def get_url_base(self):
        return self._url_base

    def get_path(self, *, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any], next_page_token: Mapping[str, Any]) -> str:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        return self._path.eval(dict(), self._config, **kwargs)

    def get_method(self):
        return self._method
