#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping, Optional

import pendulum
import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth

API_VERSION = "4.0"


@dataclass
class LookerAuthenticator(NoAuth):

    """
    Authenticator that sets the Authorization header on the HTTP requests sent using access token which is updated upon expiration.

    The header is of the form:
    `"Authorization": "token <access_token>"`

    Attributes:
        config (Config): The user-provided configuration as specified by the source's spec
    """

    config: Mapping[str, Any]

    def __post_init__(self, config):
        self._access_token = None
        self._token_expiry_date = pendulum.now()

    def update_access_token(self) -> Optional[str]:
        domain = self.config.get("domain")
        client_id = self.config.get("client_id")
        client_secret = self.config.get("client_secret")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        url = f"https://{domain}/api/{API_VERSION}/login"
        try:
            resp = requests.post(url=url, headers=headers, data=f"client_id={client_id}&client_secret={client_secret}")
            if resp.status_code != 200:
                raise LookerException("auth error: Unable to connect to the Looker API. Please check your credentials.")
        except ConnectionError as error:
            raise LookerException(f"auth error: {str(error)}")
        data = resp.json()
        self._access_token = data["access_token"]
        self._token_expiry_date = pendulum.now().add(seconds=data["expires_in"])

    def get_auth_header(self) -> Mapping[str, Any]:
        if self._token_expiry_date < pendulum.now():
            self.update_access_token()
        return {"Authorization": f"token {self._access_token}"}


class LookerException(Exception):
    pass
