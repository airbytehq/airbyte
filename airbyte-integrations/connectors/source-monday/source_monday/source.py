#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import os
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


# Basic full refresh stream
class MondayStream(HttpStream, ABC):
    url_base: str = "https://api.monday.com/v2"
    primary_key: str = "id"
    page: int = 1
    limit: Optional[int] = None
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json().get("data", {})
        records = json_response.get(self.name.lower(), [])
        self.page += 1
        if records:
            return {"page": self.page}

    def load_schema(self):
        """
        Load schema from file and make a GraphQL query
        """
        script_dir = os.path.dirname(__file__)
        schema_path = os.path.join(script_dir, f"schemas/{self.name.lower()}.json")
        with open(schema_path) as f:
            schema_dict = json.load(f)
            schema = schema_dict["properties"]
            graphql_schema = []
            for col in schema:
                if "properties" in schema[col]:
                    nested_ids = ",".join(schema[col]["properties"])
                    graphql_schema.append(f"{col}{{{nested_ids}}}")
                else:
                    graphql_schema.append(col)
        return ",".join(graphql_schema)

    def should_retry(self, response: requests.Response) -> bool:
        # Monday API return code 200 with and errors key if complexity is too high.
        # https://api.developer.monday.com/docs/complexity-queries
        is_complex_query = response.json().get("errors")
        if is_complex_query:
            self.logger.error(response.text)
        return response.status_code == 429 or 500 <= response.status_code < 600 or is_complex_query

    @property
    def retry_factor(self) -> int:
        return 15

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        graphql_params = {}
        if self.limit:
            graphql_params["limit"] = self.limit
        if next_page_token:
            graphql_params.update(next_page_token)

        graphql_query = ",".join([f"{k}:{v}" for k, v in graphql_params.items()])
        # Monday uses a query string to pass in environments
        params = {"query": f"query {{ {self.name.lower()} ({graphql_query}) {{ {self.load_schema()} }} }}"}
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json().get("data", {})
        records = json_response.get(self.name.lower(), [])
        yield from records

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return ""


class Items(MondayStream):
    """
    API Documentation: https://api.developer.monday.com/docs/items-queries
    """

    limit = 100

    @property
    def retry_factor(self) -> int:
        # this stream has additional rate limits, please see https://api.developer.monday.com/docs/items-queries#additional-rate-limit
        return 30


class Boards(MondayStream):
    """
    API Documentation: https://api.developer.monday.com/docs/groups-queries#groups-queries
    """


class Teams(MondayStream):
    """
    API Documentation: https://api.developer.monday.com/docs/teams-queries
    """

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        # Stream teams doesn't support pagination
        params = {"query": f"query {{ {self.name.lower()} () {{ {self.load_schema()} }} }}"}
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return {}


class Updates(MondayStream):
    """
    API Documentation: https://api.developer.monday.com/docs/updates-queries
    """


class Users(MondayStream):
    """
    API Documentation: https://api.developer.monday.com/docs/users-queries-1
    """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Stream Users doesn't support pagination
        return


class MondayAuthentication:
    """Provides the authentication capabilities for both old and new methods."""

    def __init__(self, config: Dict):
        self.config = config

    def get_token(self):
        # the old config supports for backward capability
        token = self.config.get("api_token")
        if not token:
            auth_type = self.config["credentials"]["auth_type"]
            if auth_type == "oauth2.0":
                token = self.config["credentials"]["access_token"]
            if auth_type == "api_token":
                token = self.config["credentials"]["api_token"]
        return token

    def get_auth(self) -> TokenAuthenticator:
        """Return the TokenAuthenticator object with access or api token."""
        return TokenAuthenticator(token=self.get_token())


class SourceMonday(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url = "https://api.monday.com/v2"
        params = {"query": "query { me { is_guest created_at name id}}"}
        auth_header = MondayAuthentication(config).get_auth().get_auth_header()
        try:
            response = requests.post(url, params=params, headers=auth_header)
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = MondayAuthentication(config).get_auth()
        return [
            Items(authenticator=auth),
            Boards(authenticator=auth),
            Teams(authenticator=auth),
            Updates(authenticator=auth),
            Users(authenticator=auth),
        ]
