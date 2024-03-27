#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import base64
import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Callable, MutableMapping


import requests
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.core import Stream, StreamData, package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader

from .exception import AvailableFieldsAccessDeniedError, CustomFieldsAccessDeniedError, NullFieldsError
from .utils import convert_custom_reports_fields_to_list, validate_custom_fields, generate_dates_to_today


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

class BambooHrIncrementalStream(BambooHrStream):
    cursor_field = "created"

    def __init__(self, config: Mapping[str, Any]) -> None:
        super().__init__(config)
        self.start_date = self.config["start_date"]
        
    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        if not current_stream_state:
            current_stream_state = {self.cursor_field: self.start_date}
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}
    

class MetaFieldsStream(BambooHrStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "meta/fields"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class EmployeesDirectory(BambooHrStream):
    primary_key = "id"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["employees"]

    def path(self, **kwargs) -> str:
        return "employees/directory"


class CustomReportsStream(BambooHrStream):
    primary_key = None

    def __init__(self, *args, **kwargs):
        self._schema = None
        super().__init__(*args, **kwargs)

    @property
    def schema(self):
        if not self._schema:
            self._schema = self.get_json_schema()
        return self._schema

    def _get_json_schema_from_config(self):
        if self.config.get("custom_reports_fields"):
            properties = {
                field.strip(): {"type": ["null", "string"]}
                for field in convert_custom_reports_fields_to_list(self.config.get("custom_reports_fields", ""))
            }
        else:
            properties = {}
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
        }

    def _get_json_schema_from_file(self):
        return super().get_json_schema()

    @staticmethod
    def _union_schemas(schema1, schema2):
        schema1["properties"] = {**schema1["properties"], **schema2["properties"]}
        return schema1

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Returns the JSON schema.

        The final schema is constructed by first generating a schema for the fields
        in the config and, if default fields should be included, adding these to the
        schema.
        """
        schema = self._get_json_schema_from_config()
        if self.config.get("custom_reports_include_default_fields"):
            default_schema = self._get_json_schema_from_file()
            schema = self._union_schemas(default_schema, schema)
        return schema

    def path(self, **kwargs) -> str:
        return "reports/custom"

    @property
    def http_method(self) -> str:
        return "POST"

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return {"title": "Airbyte", "fields": list(self.schema["properties"].keys())}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["employees"]


class TimeOffRequests(BambooHrIncrementalStream):

    primary_key = "id"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


    def path(self, date_from, **kwargs):
        return f"time_off/requests/?start={date_from}&end={date_from}"
        

    def send_request(
        self,
        start_date: str,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:        
        request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        path = self.path(date_from =start_date,stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        headers = dict(request_headers, **self.authenticator.get_auth_header())
        request = self._create_prepared_request(path= path, headers= headers)
        response = self._send_request(request, {})
        return request, response
    
    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        actual_record = {key: value for key, value in record.items() if key in self.get_json_schema()["properties"].keys()}
        return actual_record

    def _read_pages(
        self,
        records_generator_fn: Callable[
            [requests.PreparedRequest, requests.Response, Mapping[str, Any], Optional[Mapping[str, Any]]], Iterable[StreamData]
        ],
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        stream_state = stream_state or {}
        for start_date in generate_dates_to_today(self.start_date):
            request, response = self.send_request(start_date, stream_slice, stream_state, None)
            for record in records_generator_fn(request, response, stream_state, stream_slice):
                yield self.transform(record)

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
        return [
            CustomReportsStream(config),
            EmployeesDirectory(config),
            TimeOffRequests(config)
        ]
