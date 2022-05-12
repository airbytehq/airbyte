#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Mapping, MutableMapping

from airbyte_cdk.sources.cac.requesters.request_params.request_parameters_provider import RequestParameterProvider
from airbyte_cdk.sources.cac.requesters.requester import Requester


class HttpRequester(Requester):
    def __init__(
        self,
        url_base,
        path,
        method,
        request_parameters_provider: RequestParameterProvider,
        authenticator,
        vars=None,
        config=None,
    ):
        if vars is None:
            vars = dict()
        if config is None:
            config = dict()
        self._vars = vars
        self._config = config
        self._authenticator = authenticator
        self._url_base = url_base
        self._path = path
        self._method = method
        self._request_parameters_provider = request_parameters_provider

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return self._request_parameters_provider.request_params(stream_state, stream_slice, next_page_token)

    def get_authenticator(self):
        return self._authenticator

    def get_url_base(self):
        return self._url_base

    def get_path(self):
        return self._path

    def get_method(self):
        return self._method
