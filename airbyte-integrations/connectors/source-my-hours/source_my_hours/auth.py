#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping, MutableMapping, Tuple

import pendulum
import requests
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import Oauth2Authenticator

from .constants import REQUEST_HEADERS, URL_BASE


class MyHoursAuthenticator(Oauth2Authenticator):
    def __init__(self, email: str, password: str):
        super().__init__(
            token_refresh_endpoint=f"{URL_BASE}/tokens/refresh",
            client_id=None,
            client_secret=None,
            refresh_token=None,
            access_token_name="accessToken",
            expires_in_name="expiresIn",
        )

        self.retrieve_refresh_token(email, password)

    def retrieve_refresh_token(self, email: str, password: str):
        t0 = pendulum.now()
        payload = json.dumps({"grantType": "password", "email": email, "password": password, "clientId": "api"})
        response = requests.post(f"{URL_BASE}/tokens/login", headers=REQUEST_HEADERS, data=payload)
        response.raise_for_status()
        json_response = response.json()

        self.refresh_token = json_response["refreshToken"]
        self._access_token = json_response[self.access_token_name]
        self._token_expiry_date = t0.add(seconds=json_response[self.expires_in_name])

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {
            "grantType": "refresh_token",
            "refreshToken": self.refresh_token,
        }

        return payload

    def refresh_access_token(self) -> Tuple[str, int]:
        try:
            response = requests.request(method="POST", url=self.token_refresh_endpoint, data=self.get_refresh_request_body())
            response.raise_for_status()
            response_json = response.json()
            self.refresh_token = response_json["refreshToken"]
            return response_json[self.access_token_name], response_json[self.expires_in_name]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
