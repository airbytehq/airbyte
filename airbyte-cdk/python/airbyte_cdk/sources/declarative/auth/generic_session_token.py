#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import base64
import datetime
import logging
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union

import dpath.util
import pendulum
import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import ApiKeyAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.types import Config
from cachetools import TTLCache, cached
from isodate import Duration, parse_duration
from pendulum import DateTime

SESSION_TOKEN_CONFIG_KEY = "__session_token"


@dataclass
class GenericSessionTokenAuthenticator(DeclarativeAuthenticator):
    login_requester: Requester
    session_token_path: List[str]
    data_request_authenticator: Union[BearerAuthenticator, ApiKeyAuthenticator]
    expiration_time: Union[datetime.timedelta, Duration]
    parameters: InitVar[Mapping[str, Any]]

    _decoder: Decoder = JsonDecoder(parameters={})
    _next_expiration_time: Optional[DateTime] = None

    @property
    def auth_header(self) -> str:
        return self.data_request_authenticator.auth_header

    @property
    def token(self) -> str:
        self._refresh_if_necessary()
        return self.data_request_authenticator.token

    def get_request_params(self) -> Optional[Mapping[str, Any]]:
        self._refresh_if_necessary()
        return self.data_request_authenticator.get_request_params()

    def get_request_body_data(self) -> Optional[Union[Mapping[str, Any], str]]:
        self._refresh_if_necessary()
        return self.data_request_authenticator.get_request_body_data()

    def get_request_body_json(self) -> Optional[Mapping[str, Any]]:
        self._refresh_if_necessary()
        return self.data_request_authenticator.get_request_body_json()

    def _refresh_if_necessary(self):
        if self._next_expiration_time is None or self._next_expiration_time < pendulum.now():
            self._refresh()

    def _refresh(self):
        response = self.login_requester.send_request()
        session_token = dpath.util.get(self._decoder.decode(response), self.session_token_path)
        self._next_expiration_time = pendulum.now() + self.expiration_time
        self.data_request_authenticator.config[SESSION_TOKEN_CONFIG_KEY] = session_token
