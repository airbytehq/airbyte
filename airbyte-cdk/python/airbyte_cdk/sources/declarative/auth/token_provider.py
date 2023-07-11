#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import abstractmethod
import datetime
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional, Union
from airbyte_cdk.sources.declarative.exceptions import ReadException

import dpath.util
import pendulum
import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.types import Config
from isodate import Duration
from pendulum import DateTime

SESSION_TOKEN_CONFIG_KEY = "__session_token"

class TokenProvider:
    @abstractmethod
    def get_token(self) -> str:
        pass

@dataclass
class SessionTokenProvider(TokenProvider):
    login_requester: Requester
    session_token_path: List[str]
    expiration_time: Union[datetime.timedelta, Duration]
    parameters: InitVar[Mapping[str, Any]]

    _decoder: Decoder = JsonDecoder(parameters={})
    _next_expiration_time: Optional[DateTime] = None
    _token: Optional[str] = None

    def get_token(self) -> str:
        self._refresh_if_necessary()
        return self._token

    def _refresh_if_necessary(self):
        if self._next_expiration_time is None or self._next_expiration_time < pendulum.now():
            self._refresh()

    def _refresh(self):
        response = self.login_requester.send_request()
        if response is None:
            raise ReadException("Failed to get session token, response got ignored by requester")
        session_token = dpath.util.get(self._decoder.decode(response), self.session_token_path)
        self._next_expiration_time = pendulum.now() + self.expiration_time
        self._token = session_token

@dataclass
class InterpolatedStringTokenProvider(TokenProvider):
    config: Config
    api_token: Union[InterpolatedString, str]
    parameters: Mapping[str, Any]

    def __post_init__(self):
        self._token = InterpolatedString.create(self.api_token, parameters=self.parameters)
    
    def get_token(self) -> str:
        return self._token.eval(self.config)
