#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Mapping, Union

import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config
from requests import HTTPError

# https://docs.airbyte.com/integrations/sources/my-hours
# The Bearer token generated will expire in five days


@dataclass
class CustomAuthenticator(NoAuth):
    config: Config
    email: Union[InterpolatedString, str]
    password: Union[InterpolatedString, str]

    _access_token = None
    _refreshToken = None

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._email = InterpolatedString.create(self.email, parameters=parameters).eval(self.config)
        self._password = InterpolatedString.create(self.password, parameters=parameters).eval(self.config)

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach the page access token to params to authenticate on the HTTP request"""
        if self._access_token is None or self._refreshToken is None:
            self._access_token, self._refreshToken = self.generate_access_token()
        headers = {self.auth_header: f"Bearer {self._access_token}", "Accept": "application/json", "api-version": "1.0"}
        request.headers.update(headers)
        return request

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return self._access_token

    def _get_refresh_access_token_response(self):
        url = f"https://api2.myhours.com/api/tokens/refresh"
        headers = {"Content-Type": "application/json", "api-version": "1.0", self.auth_header: f"Bearer {self._access_token}"}

        data = {
            "refreshToken": self._refreshToken,
            "grantType": "refresh_token",
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            modified_response = {
                "access_token": response.json().get("accessToken"),
                "refresh_token": response.json().get("refreshToken"),
                "expires_in": response.json().get("expiresIn"),
            }
            return modified_response
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e

    def generate_access_token(self) -> tuple[str, str]:
        try:
            headers = {"Content-Type": "application/json", "api-version": "1.0"}

            data = {
                "email": self._email,
                "password": self._password,
                "grantType": "password",
                "clientId": "api",
            }

            url = "https://api2.myhours.com/api/tokens/login"
            rest = requests.post(url, headers=headers, json=data)
            if rest.status_code != HTTPStatus.OK:
                raise HTTPError(rest.text)
            return (rest.json().get("accessToken"), rest.json().get("refreshToken"))
        except Exception as e:
            raise Exception(f"Error while generating access token: {e}") from e
