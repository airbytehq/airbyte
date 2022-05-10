#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Optional

import requests
from airbyte_cdk.sources.cac.requesters.requester import Requester


class HttpRequester(Requester):
    def __init__(self, url_base, path, method, authenticator, vars=None, config=None):
        # print("creating HttpRequester")
        if vars is None:
            vars = dict()
        if config is None:
            config = dict()
        self._authenticator = authenticator  # LowCodeComponentFactory().create_component(authenticator, vars, config)
        # print(f"authenticator: {self._authenticator.auth_method}")
        # print(f"authenticator: {self._authenticator.auth_header}")
        self._url_base = url_base
        self._path = path
        self._method = method

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
