#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from requests.auth import AuthBase


class SourceTestFixture(AbstractSource):
    """
    This is a concrete implementation of a Source connector that provides implementations of all the methods needed to run sync
    operations. For simplicity, it also overrides functions that read from files in favor of returning the data directly avoiding
    the need to load static files (ex. spec.yaml, config.json, configured_catalog.json) into the unit-test package.
    """

    def __init__(self, streams: Optional[List[Stream]] = None, authenticator: Optional[AuthBase] = None):
        self._streams = streams
        self._authenticator = authenticator

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        return ConnectorSpecification(
            connectionSpecification={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "Test Fixture Spec",
                "type": "object",
                "required": ["api_token"],
                "properties": {
                    "api_token": {
                        "type": "string",
                        "title": "API token",
                        "description": "The token used to authenticate requests to the API.",
                        "airbyte_secret": True,
                    }
                },
            }
        )

    def read_config(self, config_path: str) -> Mapping[str, Any]:
        return {"api_token": "just_some_token"}

    @classmethod
    def read_catalog(cls, catalog_path: str) -> ConfiguredAirbyteCatalog:
        return ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(
                        name="http_test_stream",
                        json_schema={},
                        supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                        default_cursor_field=["updated_at"],
                        source_defined_cursor=True,
                        source_defined_primary_key=[["id"]],
                    ),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
            ]
        )

    def check_connection(self, *args, **kwargs) -> Tuple[bool, Optional[Any]]:
        return True, ""

    def streams(self, *args, **kwargs) -> List[Stream]:
        return [HttpTestStream(authenticator=self._authenticator)]


class HttpTestStream(HttpStream, ABC):
    url_base = "https://airbyte.com/api/v1/"

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return ["updated_at"]

    @property
    def availability_strategy(self):
        return None

    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "cast"

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        body = response.json() or {}
        return body["records"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        return {}


def fixture_mock_send(self, request, **kwargs) -> requests.Response:
    """
    Helper method that can be used by a test to patch the Session.send() function and mock the outbound send operation to provide
    faster and more reliable responses compared to actual API requests
    """
    response = requests.Response()
    response.request = request
    response.status_code = 200
    response.headers = {"header": "value"}
    response_body = {
        "records": [
            {"id": 1, "name": "Celine Song", "position": "director"},
            {"id": 2, "name": "Shabier Kirchner", "position": "cinematographer"},
            {"id": 3, "name": "Christopher Bear", "position": "composer"},
            {"id": 4, "name": "Daniel Rossen", "position": "composer"},
        ]
    }
    response._content = json.dumps(response_body).encode("utf-8")
    return response


class SourceFixtureOauthAuthenticator(Oauth2Authenticator):
    """
    Test OAuth authenticator that only overrides the request and response aspect of the authenticator flow
    """

    def refresh_access_token(self) -> Tuple[str, int]:
        response = requests.request(method="POST", url=self.get_token_refresh_endpoint(), params={})
        response.raise_for_status()
        return "some_access_token", 1800  # Mock oauth response values to be used during the data retrieval step
