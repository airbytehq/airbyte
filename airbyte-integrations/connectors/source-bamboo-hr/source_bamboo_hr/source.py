#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import base64
import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, Optional, Tuple, NamedTuple, Union

import requests
from requests.exceptions import HTTPError
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .exception import (
    AvailableFieldsAccessDeniedError,
)
from .utils import (
    chunk_iterable,
)


class BambooHrStream(HttpStream, ABC):
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = config
        super().__init__(authenticator=config["authenticator"])

    @property
    def url_base(self) -> str:
        return (
            f"https://api.bamboohr.com/api/gateway.php/{self.config['subdomain']}/v1/"
        )

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        """
        BambooHR does not support pagination.
        """
        pass


class MetaTablesStream(BambooHrStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "meta/tables"

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        yield from response.json()


class BambooMetaField(NamedTuple):
    """Immutable typed representation of what is returned from the meta/fields
    endpoint."""

    id: Union[int, str]
    name: str
    type: str
    alias: Optional[str] = None
    deprecated: Optional[bool] = None

class BambooMetaTableField(NamedTuple):
    """Immutable typed representation of the field data returned from the meta/tables
    endpoint."""
    id: int
    name: str
    alias: str
    type: str

class BambooMetaTable(NamedTuple):
    """Immutable typed representation of what is returned from the meta/tables
    endpoint."""

    alias: str
    fields: List[BambooMetaTableField]


class MetaFieldsStream(BambooHrStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "meta/fields"

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        yield from response.json()

class TablesStream(BambooHrStream):
    primary_key = None
    raise_on_http_errors = False
    skip_http_status_codes = [
        requests.codes.NOT_FOUND,
    ]

    def _convert_raw_meta_table_to_typed(raw_meta_table: Mapping[str,Any]) -> BambooMetaTable:
        return BambooMetaTable(
            alias=raw_meta_table.get("alias"),
            fields=[
                BambooMetaTableField(**field) for field in raw_meta_table.get("fields")
            ],
        )

    # def _create_one_of_schema(bamboo_meta_table: BambooMetaTable) -> Mapping[str, Any]:
    #     schema = {
    #             "" : ""
    #         }
    #     return schema

    # def get_json_schema(self) -> Mapping[str, Any]:
    #     """
    #         1. Get access to the available tables.
    #         2. Construct the Json Schema from the available tables.
               
    #     """

    #     available_tables = self.config.get("available_tables")
    #     typed_available_tables = map(self._convert_raw_meta_table_to_typed, available_tables)

    #     tables.forEach { table ->


    #     }

    #     if self._schema is None:
    #         available_tables = self.config.get("available_tables")
    #         schema = {
    #             "$schema": "http://json-schema.org/draft-07/schema#",
    #             "type": ["object"] ,
    #             "properties": {
    #                 "knoetic_table_name": {"type": "string"},
    #             },
    #         }

    #         for table in typed_available_tables:
    #             table_name = table.get("alias")
    #             fields = table.get("fields")
    #             schema["properties"][table_name] = {
    #                 "type": "object",
    #                 "properties": {
    #                     "knoetic_table_name": {"type": "string"},
    #                 },
    #             }
    #             for field in fields:
    #                 field_name = field.get("alias")
    #                 field_type = field.get("type")
    #                 schema["properties"][table_name]["properties"][field_name] = {
    #                     "type": field_type
    #                 }

    #         self._schema = schema

    #     return self._schema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        schema = self.get_json_schema()
        print(f"The schema is {schema}")

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        # Each table has an 'alias' field that we use to grab
        # all values.  See `path` method for how it's used in the URL.
        for meta_table in self.config.get("available_tables"):
            table = meta_table.get("alias")
            yield {"table": table}

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        target_table = stream_slice["table"]
        return f"employees/all/tables/{target_table}"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs,
    ) -> Iterable[Mapping]:
        table_name = stream_slice["table"]
        try:
            # This will raise an exception if the response is not 2xx
            response.raise_for_status()
            # If we're here, no issue.
            new_record = (dict(record, **{"knoetic_table_name": table_name}) for record in response.json())
            for record in new_record:
                # print("New record: ", record)
                yield record
            # yield from new_record
        except HTTPError as e:
            # If it's one of the status codes we're skipping, log a warning.
            # Otherwise, raise the exception.
            if not (
                self.skip_http_status_codes
                and e.response.status_code in self.skip_http_status_codes
            ):
                raise e
            self.logger.warning(
                f"Stream `{self.name}`. An error occurred, details: {e}. Skipping for now."
            )
            yield {}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        # table_name = stream_slice["table"]
        for record in super().read_records(
            sync_mode, cursor_field, stream_slice, stream_state
        ):
            # # Augment the record with the table name.
            # record["knoetic_table_name"] = table_name
            yield record


class CustomReportsStream(BambooHrStream):
    primary_key = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._schema = None

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for raw_fields in chunk_iterable(self.config.get("available_fields"), 100):
            fields = map(lambda field: BambooMetaField(**field), raw_fields)
            yield {"fields": fields}

    def path(self, **kwargs) -> str:
        return "reports/custom"

    @property
    def http_method(self) -> str:
        return "POST"

    @staticmethod
    def _convert_field_to_id(field: BambooMetaField) -> str:
        """Converts a BambooMetaField to an id for the custom report endpoint."""
        if field.alias is None:
            return str(id)
        else:
            return field.alias

    def request_body_json(
        self, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Optional[Mapping]:
        fields = stream_slice["fields"]
        field_ids = tuple(map(CustomReportsStream._convert_field_to_id, fields))
        return {"title": "Airbyte", "fields": field_ids}

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        yield from response.json()["employees"]


class EmployeesDirectoryStream(BambooHrStream):
    """
        This is not currently in use as per
        https://documentation.bamboohr.com/reference/get-employees-directory-1
    """
    primary_key = "id"

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        yield from response.json()["employees"]

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
            auth_method="Basic",
        )

    @staticmethod
    def add_authenticator_to_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Adds an authenticator entry to the config and returns the config.
        """
        config["authenticator"] = SourceBambooHr._get_authenticator(config["api_key"])
        return config

    def check_connection(
        self, logger: logging.Logger, config: Mapping[str, Any]
    ) -> Tuple[bool, Optional[Any]]:
        """
        Verifies the config and attempts to fetch the fields from the meta/fields endpoint.
        """
        config = SourceBambooHr.add_authenticator_to_config(config)

        available_fields = MetaFieldsStream(config).read_records(
            sync_mode=SyncMode.full_refresh
        )

        try:
            # Check to see that we get some fields back.
            next(available_fields)
            return True, None
        except StopIteration:
            return False, AvailableFieldsAccessDeniedError()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = SourceBambooHr.add_authenticator_to_config(config)

        # Grabbing these early on and sending them through the config seemed
        # simpler than passing them along as parent streams.
        available_fields = list(
            MetaFieldsStream(config).read_records(sync_mode=SyncMode.full_refresh)
        )
        available_tables = list(
            MetaTablesStream(config).read_records(sync_mode=SyncMode.full_refresh)
        )

        print("Current version: 3")

        config["available_fields"] = available_fields
        config["available_tables"] = available_tables

        return [
            MetaTablesStream(config),
            TablesStream(config),
            MetaFieldsStream(config),
            CustomReportsStream(config),
            # Keeping this around in case we ever need it, but
            # we should be able to get the same data from custom_reports.
            # EmployeesDirectoryStream
        ]
