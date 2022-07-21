#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
from typing import Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.streams.http.requests_native_auth.abtract_token import AbstractHeaderAuthenticator


class ApiKeyAuth(AbstractHeaderAuthenticator):
    def __init__(self, header: Union[InterpolatedString, str], token: Union[InterpolatedString, str], config: Config):
        self._header = InterpolatedString.create(header)
        self._token = InterpolatedString.create(token)
        self._config = config

    @property
    def auth_header(self) -> str:
        return self._header.eval(self._config)

    @property
    def token(self) -> str:
        return self._token.eval(self._config)


class BearerAuth(AbstractHeaderAuthenticator):
    def __init__(self, token: Union[InterpolatedString, str], config: Config):
        self._token = InterpolatedString.create(token)
        self._config = config

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"Bearer {self._token.eval(self._config)}"


class BasicHttpAuth(AbstractHeaderAuthenticator):
    def __init__(self, username: Union[InterpolatedString, str], config: Config, password: Union[InterpolatedString, str] = ""):
        self._username = InterpolatedString.create(username)
        self._password = InterpolatedString.create(password)
        self._config = config

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        auth_string = f"{self._username.eval(self._config)}:{self._password.eval(self._config)}".encode("utf8")
        print(f"auth_string: {auth_string}")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        print(f"b64encoded: {b64_encoded}")
        return f"Basic {b64_encoded}"
