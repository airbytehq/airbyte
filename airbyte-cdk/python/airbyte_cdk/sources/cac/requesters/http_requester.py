#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.cac.factory import LowCodeComponentFactory


class HttpRequester:
    def __init__(self, options, vars, config):
        print(f"creating HttpRequester with {options}")
        self._authenticator = LowCodeComponentFactory().build(options["authenticator"], vars, config)
        print(f"authenticator: {self._authenticator.auth_method}")
        print(f"authenticator: {self._authenticator.auth_header}")
        # print(f"authenticator: {self._authenticator._token}")
        self._url_base = options["url_base"]
        self._path = options["path"]

    def get_authenticator(self):
        return self._authenticator

    def get_url_base(self):
        return self._url_base

    def get_path(self):
        return self._path

    def merge_dicts(self, d1, d2):
        return {**d1, **d2}
