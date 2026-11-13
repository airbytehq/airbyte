#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Mapping, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


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

    def _validate_token_response(self, response: requests.Response, operation: str) -> None:
        if response.status_code == HTTPStatus.OK:
            return
        if response.status_code in (HTTPStatus.BAD_REQUEST, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            message = (
                f"My Hours rejected the {operation} for the configured email. "
                "Check the email and password, and confirm the user has permission to use the My Hours API."
            )
            failure_type = FailureType.config_error
        else:
            message = f"My Hours access token request failed with HTTP {response.status_code}."
            failure_type = (
                FailureType.transient_error
                if response.status_code == HTTPStatus.TOO_MANY_REQUESTS or 500 <= response.status_code < 600
                else FailureType.system_error
            )
        raise AirbyteTracedException(
            message=message,
            internal_message=f"HTTP {response.status_code}: {response.text}",
            failure_type=failure_type,
        )

    def _get_refresh_access_token_response(self):
        url = f"https://api2.myhours.com/api/tokens/refresh"
        headers = {"Content-Type": "application/json", "api-version": "1.0", self.auth_header: f"Bearer {self._access_token}"}

        data = {
            "refreshToken": self._refreshToken,
            "grantType": "refresh_token",
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            self._validate_token_response(response, "access token refresh")
            modified_response = {
                "access_token": response.json().get("accessToken"),
                "refresh_token": response.json().get("refreshToken"),
                "expires_in": response.json().get("expiresIn"),
            }
            return modified_response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            raise AirbyteTracedException(
                message="Connection to the My Hours API failed.",
                internal_message=type(e).__name__,
                failure_type=FailureType.transient_error,
            ) from e

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
            self._validate_token_response(rest, "login")
            return (rest.json().get("accessToken"), rest.json().get("refreshToken"))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            raise AirbyteTracedException(
                message="Connection to the My Hours API failed.",
                internal_message=type(e).__name__,
                failure_type=FailureType.transient_error,
            ) from e
