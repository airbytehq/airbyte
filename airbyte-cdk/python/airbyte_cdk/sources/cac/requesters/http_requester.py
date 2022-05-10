#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation
from airbyte_cdk.sources.cac.requesters.requester import Requester


class HttpRequester(Requester):
    def __init__(self, url_base, path, method, request_parameters, authenticator, vars=None, config=None):
        # print("creating HttpRequester")
        if vars is None:
            vars = dict()
        if config is None:
            config = dict()
        self._vars = vars
        self._config = config
        self._authenticator = authenticator  # LowCodeComponentFactory().create_component(authenticator, vars, config)
        # print(f"authenticator: {self._authenticator.auth_method}")
        # print(f"authenticator: {self._authenticator.auth_header}")
        self._url_base = url_base
        self._path = path
        self._method = method
        self._interpolation = JinjaInterpolation()
        self._request_parameters = request_parameters

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}

        return {
            self._interpolation.eval(name, self._vars, self._config, **kwargs): self._interpolation.eval(
                value, self._vars, self._config, **kwargs
            )
            for name, value in self._request_parameters.items()
        }

    def get_authenticator(self):
        return self._authenticator

    def get_url_base(self):
        return self._url_base

    def get_path(self):
        return self._path

    def get_method(self):
        return self._method

    def get_last_response(self) -> Optional[requests.Response]:
        return None
