#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

import requests
from requests.auth import HTTPBasicAuth

from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class OutbrainAmplifyAuthenticator(TokenAuthenticator):
    def __init__(self, config, url_base):
        self.config = config
        self.url_auth = url_base + "login"
        self.token = ""

    def generate_cache_token(
        self,
    ):
        r = requests.get(
            self.url_auth,
            auth=HTTPBasicAuth(self.config.get("credentials").get("username"), self.config.get("credentials").get("password")),
        )
        if r.status_code == 200:
            self.token = r.json().get("OB-TOKEN-V1")
        else:
            raise ConnectionError(r.json().get("message"))

    def get_auth_header(self) -> Mapping[dict, Any]:
        if self.config.get("credentials").get("type") == "access_token":
            self.token = self.config.get("credentials").get("access_token")
            return {"OB-TOKEN-V1": "{}".format(self.token)}
        else:
            if self.token:
                return {"OB-TOKEN-V1": "{}".format(self.token)}
            else:
                self.generate_cache_token()
                return {"OB-TOKEN-V1": "{}".format(self.token)}
