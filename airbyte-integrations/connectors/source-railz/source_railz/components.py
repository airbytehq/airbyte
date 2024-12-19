#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import time
from dataclasses import InitVar, dataclass
from typing import Any, Iterable, Mapping, Optional, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.stream_slicers import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator
from isodate import Duration, parse_duration


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


@dataclass
class NestedStateCartesianProductStreamSlicer(CartesianProductStreamSlicer):
    """
    [Low-Code Custom Component] NestedStateCartesianProductStreamSlicer
    https://github.com/airbytehq/airbyte/issues/22873

    Some streams require support of nested state:
    {
      "accounting_transactions": {
        "Business1": {
          "dynamicsBusinessCentral": {
            "postedDate": "2022-12-28T00:00:00.000Z"
          }
        },
        "Business2": {
          "oracleNetsuite": {
            "postedDate": "2022-12-28T00:00:00.000Z"
          }
        }
      }
    }
    """

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._cursor = {}
        self._parameters = parameters

    def get_stream_state(self) -> Mapping[str, Any]:
        return self._cursor

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        connections_slicer, datetime_slicer = self.stream_slicers
        for connection_slice in connections_slicer.stream_slices(sync_mode, stream_state):
            businessName = connection_slice["connection"]["businessName"]
            serviceName = connection_slice["connection"]["serviceName"]
            datetime_slicer._cursor = None
            for datetime_slice in datetime_slicer.stream_slices(sync_mode, stream_state.get(businessName, {}).get(serviceName, {})):
                yield connection_slice | datetime_slice

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        datetime_slicer = self.stream_slicers[1]
        datetime_slicer.update_cursor(stream_slice, last_record)
        if last_record:
            businessName = stream_slice["connection"]["businessName"]
            serviceName = stream_slice["connection"]["serviceName"]
            self._cursor.setdefault(businessName, {}).setdefault(serviceName, {}).update(datetime_slicer.get_stream_state())
        else:
            self._cursor = stream_slice
