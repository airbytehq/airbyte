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

from .exception import AvailableFieldsAccessDeniedError, CustomFieldsAccessDeniedError, NullFieldsError
from .utils import convert_custom_reports_fields_to_list, validate_custom_fields, chunk_iterable


class BambooHrStream(HttpStream, ABC):
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


class MetaFieldsStream(BambooHrStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "meta/fields"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()

class MetaTablesStream(BambooHrStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "meta/tables"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class BambooMetaField(NamedTuple):
    """Immutable typed representation of what is returned from the meta/fields
    endpoint."""
    id: Union[int, str]
    name: str
    type: str
    alias: Optional[str] = None
    deprecated: Optional[bool] = None

class TablesStream(BambooHrStream):
    primary_key = None
    raise_on_http_errors = False
    skip_http_status_codes = [
        requests.codes.NOT_FOUND,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._schema = None

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        # Each table has an 'alias' field that we use to grab
        # all values.  See `path` method for how it's used in the URL.
        for meta_table in self.config.get('available_tables'):
            table = meta_table.get('alias')
            yield {"table": table}

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        target_table = stream_slice["table"]
        return f"employees/all/tables/{target_table}"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        try :
            # This will raise an exception if the response is not 2xx
            response.raise_for_status()
            yield from response.json()
        except HTTPError as e:
            # If it's one of the status codes we're skipping, log a warning.
            # Otherwise, raise the exception.
            if not (self.skip_http_status_codes and e.response.status_code in self.skip_http_status_codes):
                raise e
            self.logger.warning(f"Stream `{self.name}`. An error occurred, details: {e}. Skipping for now.")
            yield {}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        table_name = stream_slice["table"]
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            # Augment the record with the table name.
            record["knoetic_table_name"] = table_name
            yield record
class CustomReportsStream(BambooHrStream):
    primary_key = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._schema = None

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for raw_fields in chunk_iterable(self.config.get('available_fields'), 100):
            fields = map(lambda field: BambooMetaField(**field), raw_fields)
            yield {"fields": fields}

    # @property
    # def schema(self):
    #     if not self._schema:
    #         self._schema = self.get_json_schema()
    #     return self._schema

    # def _get_json_schema_from_config(self):
    #     if self.config.get("custom_reports_fields"):
    #         properties = {
    #             field.strip(): {"type": ["null", "string"]}
    #             for field in convert_custom_reports_fields_to_list(self.config.get("custom_reports_fields", ""))
    #         }
    #     else:
    #         properties = {}
    #     return {
    #         "$schema": "http://json-schema.org/draft-07/schema#",
    #         "type": "object",
    #         "properties": properties,
    #     }

    # def _get_json_schema_from_file(self):
    #     return super().get_json_schema()

    # @staticmethod
    # def _union_schemas(schema1, schema2):
    #     schema1["properties"] = {**schema1["properties"], **schema2["properties"]}
    #     return schema1

    # def get_json_schema(self) -> Mapping[str, Any]:
    #     """
    #     Returns the JSON schema.

    #     The final schema is constructed by first generating a schema for the fields
    #     in the config and, if default fields should be included, adding these to the
    #     schema.
    #     """
    #     schema = self._get_json_schema_from_config()
    #     if self.config.get("custom_reports_include_default_fields"):
    #         default_schema = self._get_json_schema_from_file()
    #         schema = self._union_schemas(default_schema, schema)
    #     return schema

    def path(self, **kwargs) -> str:
        return "reports/custom"

    @property
    def http_method(self) -> str:
        return "POST"

    @staticmethod
    def _convert_field_to_id(field:BambooMetaField) -> str:
        """Converts a BambooMetaField to an id for the custom report endpoint."""
        if field.alias is None:
            return str(id)
        else:
            return field.alias


    def request_body_json(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Optional[Mapping]:
        fields = stream_slice["fields"]
        field_ids = tuple(map(CustomReportsStream._convert_field_to_id, fields))
        return {"title": "Airbyte", "fields": field_ids}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["employees"]


class SourceBambooHr(AbstractSource):
    @staticmethod
    def _get_authenticator(api_key):
        """
        Returns a TokenAuthenticator.

        The API token is concatenated with `:x` and the resulting string is base-64 encoded.
        See https://documentation.bamboohr.com/docs#authentication
        """
        return TokenAuthenticator(token=base64.b64encode(f"{api_key}:x".encode("utf-8")).decode("utf-8"), auth_method="Basic")

    @staticmethod
    def add_authenticator_to_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Adds an authenticator entry to the config and returns the config.
        """
        config["authenticator"] = SourceBambooHr._get_authenticator(config["api_key"])
        return config

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Verifies the config and attempts to fetch the fields from the meta/fields endpoint.
        """
        config = SourceBambooHr.add_authenticator_to_config(config)

        if not config.get("custom_reports_fields") and not config.get("custom_reports_include_default_fields"):
            return False, NullFieldsError()

        available_fields = MetaFieldsStream(config).read_records(sync_mode=SyncMode.full_refresh)
        custom_fields = convert_custom_reports_fields_to_list(config.get("custom_reports_fields", ""))
        denied_fields = validate_custom_fields(custom_fields, available_fields)

        if denied_fields:
            return False, CustomFieldsAccessDeniedError(denied_fields)


        try:
            next(available_fields)
            return True, None
        except StopIteration:
            return False, AvailableFieldsAccessDeniedError()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = SourceBambooHr.add_authenticator_to_config(config)

        # Grabbing these early on and sending them through the config seemed
        # simpler than passing them along as parent streams.
        available_fields = list(MetaFieldsStream(config).read_records(sync_mode=SyncMode.full_refresh))
        available_tables = list(MetaTablesStream(config).read_records(sync_mode=SyncMode.full_refresh))

        config["available_fields"] = available_fields
        config["available_tables"] = available_tables

        return [
            MetaTablesStream(config),
            TablesStream(config),
            MetaFieldsStream(config),
            CustomReportsStream(config),
        ]
