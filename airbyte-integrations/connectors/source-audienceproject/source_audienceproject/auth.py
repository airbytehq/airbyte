#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from json.decoder import JSONDecodeError
from typing import Any, Mapping

import requests
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class AudienceProjectAuthenticator(TokenAuthenticator):
    def __init__(self, config: Mapping[str, Any], url_base: str):
        self.config = config
        self.token_url_auth = url_base + "oauth/access_token"
        self.validate_url_auth = url_base + "oauth/validate_token"
        self.token = ""

    def generate_cache_token(self):
        if self.config.get("credentials").get("type") == "access_token":
            self.token = self.config.get("credentials").get("access_token")
            if not self.validate_token(self.token):
                raise ConnectionError("Unauthorized Token")
        if self.config.get("credentials").get("type") == "OAuth":
            if not self.token or not self.validate_token(self.token):
                try:
                    response = requests.post(
                        url=self.token_url_auth,
                        params={
                            "client_id": self.config.get("credentials").get("client_id"),
                            "client_secret": self.config.get("credentials").get("client_secret"),
                            "grant_type": "client_credentials",
                        },
                    )
                    response.raise_for_status()
                    self.token = response.json().get("access_token")
                except JSONDecodeError:
                    raise ConnectionError(response.text)

    def validate_token(self, access_token: str) -> bool:
        validate_url_base = self.validate_url_auth
        # time.sleep(5)
        response = requests.post(url=validate_url_base, params={"access_token": access_token})
        if response.status_code == 200:
            authorization = response.json().get("authorized")
            if not authorization:
                return False
            return True
        else:
            return False

    def get_auth_header(self) -> Mapping[dict, Any]:
        self.generate_cache_token()
        return {"Authorization": "Bearer " + "{}".format(self.token)}
