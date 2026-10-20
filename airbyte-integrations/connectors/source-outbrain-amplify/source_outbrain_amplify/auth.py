#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests
from requests.auth import HTTPBasicAuth

from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator


class OutbrainAmplifyAuthenticator(AbstractHeaderAuthenticator):
    def __init__(self, config, url_base):
        self.config = config
        self.url_auth = url_base + "login"
        self._token = ""

    def generate_cache_token(
        self,
    ):
        r = requests.get(
            self.url_auth,
            auth=HTTPBasicAuth(self.config.get("credentials").get("username"), self.config.get("credentials").get("password")),
        )
        if r.status_code == 200:
            self._token = r.json().get("OB-TOKEN-V1")
        else:
            raise ConnectionError(r.json().get("message"))

    @property
    def auth_header(self) -> str:
        return "OB-TOKEN-V1"

    @property
    def token(self) -> str:
        if self.config.get("credentials").get("type") == "access_token":
            return self.config.get("credentials").get("access_token")
        if not self._token:
            self.generate_cache_token()
        return self._token
