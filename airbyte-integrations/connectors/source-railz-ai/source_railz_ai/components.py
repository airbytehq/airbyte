#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import time
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Union

import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config, Record
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator
from dataclasses_jsonschema import JsonSchemaMixin
from isodate import Duration, parse_duration


@dataclass
class ShortLivedTokenAuthenticator(AbstractHeaderAuthenticator, DeclarativeAuthenticator, JsonSchemaMixin):
    """
    https://docs.railz.ai/reference/authentication
    """

    client_id: Union[InterpolatedString, str]
    secret_key: Union[InterpolatedString, str]
    url: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]
    token_key: Union[InterpolatedString, str] = "access_token"
    lifetime: Union[InterpolatedString, str] = "PT3600S"

    def __post_init__(self, options: Mapping[str, Any]):
        self._client_id = InterpolatedString.create(self.client_id, options=options)
        self._secret_key = InterpolatedString.create(self.secret_key, options=options)
        self._url = InterpolatedString.create(self.url, options=options)
        self._token_key = InterpolatedString.create(self.token_key, options=options)
        self._lifetime = InterpolatedString.create(self.lifetime, options=options)
        self._basic_auth = BasicHttpAuthenticator(
            username=self._client_id,
            password=self._secret_key,
            config=self.config,
            options=options,
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
class RailzNestedExtractor(RecordExtractor, JsonSchemaMixin):
    config: Config
    options: InitVar[Mapping[str, Any]]
    nested_fields: List[Union[InterpolatedString, str]]
    propagate_fields: List[Union[InterpolatedString, str]]
    prefix_key: Union[InterpolatedString, str] = None

    def __post_init__(self, options: Mapping[str, Any]):
        self._nested_fields = [InterpolatedString.create(nested_field, options=options) for nested_field in self.nested_fields]
        if not self._nested_fields:
            ValueError("nested_fields cannot be empty")
        self._propagate_fields = [InterpolatedString.create(propagate_field, options=options) for propagate_field in self.propagate_fields]
        self._prefix_key = self.prefix_key
        if self.prefix_key:
            self._prefix_key = InterpolatedString.create(self.prefix_key, options=options)

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_json = response.json()
        nested_fields = [f.eval(self.config) for f in self._nested_fields]
        propagate_fields = [f.eval(self.config) for f in self._propagate_fields]
        prefix_key = self._prefix_key
        if self._prefix_key:
            prefix_key = self._prefix_key.eval(self.config)
        records = []
        for record in self._extract_records(response_json, nested_fields, propagate_fields):
            if prefix_key:
                record = {prefix_key: record}
            records.append(record)
        return records

    def _extract_records(self, obj, nested_fields, propagate_fields=None):
        field = nested_fields.pop(0)
        for record in obj[field]:
            for propagate_field in propagate_fields:
                if propagate_field in obj:
                    record[propagate_field] = obj[propagate_field]
            if nested_fields:
                yield from self._extract_records(record, nested_fields[:], propagate_fields)
            else:
                yield record
