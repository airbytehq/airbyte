#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Union

import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator
from cachetools import TTLCache, cached
from dataclasses_jsonschema import JsonSchemaMixin

cacheMetabase = TTLCache(maxsize=1000, ttl=86400)


@cached(cacheMetabase)
def get_new_session_token(api_url: str, username: str, password: str) -> str:
    response = requests.post(
        f"{api_url}",
        headers={"Content-Type": "application/json"},
        json={"username": username, "password": password},
    )
    response.raise_for_status()
    if not response.ok:
        raise ConnectionError(f"Failed to retrieve new session token, response code {response.status_code} because {response.reason}")
    return response.json()["id"]


@dataclass
class MetabaseSessionTokenAuthenticator(AbstractHeaderAuthenticator, DeclarativeAuthenticator, JsonSchemaMixin):
    api_url: Union[InterpolatedString, str]
    session_token: Union[InterpolatedString, str]
    username: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]
    password: Union[InterpolatedString, str] = ""

    def __post_init__(self, options):
        self._username = InterpolatedString.create(self.username, options=options)
        self._password = InterpolatedString.create(self.password, options=options)
        self._api_url = InterpolatedString.create(self.api_url, options=options)
        self._session_token = InterpolatedString.create(self.session_token, options=options)
        self.logger = logging.getLogger("airbyte")

    @property
    def auth_header(self) -> str:
        return "X-Metabase-Session"

    @property
    def token(self) -> str:
        if self._session_token.eval(self.config):
            if self.is_valid_session_token():
                return self._session_token.eval(self.config)
        if self._password.eval(self.config) and self._username.eval(self.config):
            username = self._username.eval(self.config)
            password = self._password.eval(self.config)
            api_url = f"{self._api_url.eval(self.config)}session"

            return get_new_session_token(api_url, username, password)

        raise ConnectionError("Invalid credentials: session token is not valid or provide username and password")

    def is_valid_session_token(self) -> bool:
        try:
            response = requests.get(
                f"{self._api_url.eval(self.config)}user/current", headers={self.auth_header: self._session_token.eval(self.config)}
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == requests.codes["unauthorized"]:
                self.logger.warning(f"Unable to connect to Metabase source due to {str(e)}")
                return False
            else:
                raise ConnectionError(f"Error while validating session token: {e}")
        if response.ok:
            json_response = response.json()
            self.logger.info(
                f"Connection check for Metabase successful for {json_response['common_name']} login at {json_response['last_login']}"
            )
            return True
        else:
            raise ConnectionError(f"Failed to retrieve new session token, response code {response.status_code} because {response.reason}")
