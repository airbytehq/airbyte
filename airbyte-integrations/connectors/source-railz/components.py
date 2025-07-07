#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import time
from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Union

import requests
from isodate import Duration, parse_duration

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class ShortLivedTokenAuthenticator(DeclarativeAuthenticator):
    """
    [Low-Code Custom Component] ShortLivedTokenAuthenticator
    https://github.com/airbytehq/airbyte/issues/22872

    https://docs.railz.ai/reference/authentication
    """

    client_id: Union[InterpolatedString, str]
    secret_key: Union[InterpolatedString, str]
    url: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    token_key: Union[InterpolatedString, str] = "access_token"
    lifetime: Union[InterpolatedString, str] = "PT3600S"

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._client_id = InterpolatedString.create(self.client_id, parameters=parameters)
        self._secret_key = InterpolatedString.create(self.secret_key, parameters=parameters)
        self._url = InterpolatedString.create(self.url, parameters=parameters)
        self._token_key = InterpolatedString.create(self.token_key, parameters=parameters)
        self._lifetime = InterpolatedString.create(self.lifetime, parameters=parameters)
        self._basic_auth = BasicHttpAuthenticator(
            username=self._client_id,
            password=self._secret_key,
            config=self.config,
            parameters=parameters,
        )
        self._session = requests.Session()
        self._token = None
        self._timestamp = None

    @classmethod
    def _parse_timedelta(cls, time_str) -> Union[datetime.timedelta, Duration]:
        """
        :return Parses an ISO 8601 durations into datetime.timedelta or Duration objects.
        """
        if not time_str:
            return datetime.timedelta(0)
        return parse_duration(time_str)

    def check_token(self):
        now = time.time()
        url = self._url.eval(self.config)
        token_key = self._token_key.eval(self.config)
        lifetime = self._parse_timedelta(self._lifetime.eval(self.config))
        if not self._token or now - self._timestamp >= lifetime.seconds:
            response = self._session.get(url, headers=self._basic_auth.get_auth_header())
            response.raise_for_status()
            response_json = response.json()
            if token_key not in response_json:
                raise Exception(f"token_key: '{token_key}' not found in response {url}")
            self._token = response_json[token_key]
            self._timestamp = now

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        self.check_token()
        return f"Bearer {self._token}"
