#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import base64
import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class BambooHrStream(HttpStream, ABC):
    primary_key = "id"

    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = config
        super().__init__(authenticator=config["authenticator"])

    @property
    def url_base(self) -> str:
        return f"https://api.bamboohr.com/api/gateway.php/{self.config['subdomain']}/v1/"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        BambooHR does not support pagination.
        """
        pass

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class MetaFieldsStream(BambooHrStream):
    def path(self, **kwargs) -> str:
        return "meta/fields"


class EmployeesDirectoryStream(BambooHrStream):
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Logic taken from the previous implementation.
        https://github.com/airbytehq/airbyte/blob/387d6d05453eab73968cbb6c8170d7d8d0dd25bc/airbyte-integrations/connectors/source-bamboo-hr/source_bamboo_hr/source.py#L98
        """
        records = MetaFieldsStream(config=self.config).read_records(sync_mode=SyncMode.full_refresh)
        properties = {}
        for record in records:
            properties[record.get("alias", record["name"])] = {"type": ["null", "string"]}
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
        }

    def path(self, **kwargs) -> str:
        return "employees/directory"


class SourceBambooHr(AbstractSource):
    @staticmethod
    def _get_authenticator(api_key):
        """
        Returns a TokenAuthenticator.

        The API token is concatenated with `:x` and the resulting string is base-64 encoded.
        See https://documentation.bamboohr.com/docs#authentication
        """
        return TokenAuthenticator(
            token=base64.b64encode(f"{api_key}:x".encode("utf-8")).decode("utf-8"),
            auth_method="Basic"
        )

    @staticmethod
    def add_authenticator_to_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Adds an authenticator entry to the config and returns the config.
        """
        config["authenticator"] = SourceBambooHr._get_authenticator(config["api_key"])
        return config

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Attempts to fetch the fields from the meta/fields endpoint.
        """
        config = SourceBambooHr.add_authenticator_to_config(config)
        try:
            list(MetaFieldsStream(config).read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = SourceBambooHr.add_authenticator_to_config(config)
        return [
            EmployeesDirectoryStream(config),
        ]
