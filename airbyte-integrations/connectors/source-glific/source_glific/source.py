#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, Optional, Tuple
import json
from datetime import datetime
import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.core import StreamData


stream_json_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "id": {
            "type": [
                "number",
            ]
        },
        "updated_at": {"type": ["string", "null"]},
        "data": {
            "type": "object",
        },
    },
}


# Basic full refresh stream
class GlificStream(HttpStream, ABC):
    primary_key = "id"
    cursor_value = None
    latest_updated_date = None

    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class GlificStream(HttpStream, ABC)` which is the current class
    `class Customers(GlificStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(GlificStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalGlificStream((GlificStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    def __init__(self, stream_name: str, url_base: str, pagination_limit: int, credentials: dict, config: dict, **kwargs):
        super().__init__(**kwargs)

        self.stream_name = stream_name
        self.api_url = url_base
        self.credentials = credentials
        self.pagination_limit = pagination_limit
        self.start_time = config["start_time"]
        self.offset = 0
        self.last_record = None

    @property
    def url_base(self) -> str:
        return self.api_url

    @property
    def name(self) -> str:
        return self.stream_name

    @property
    def http_method(self) -> str:
        """All requests in the glific stream are posts with body"""
        return "POST"

    def get_json_schema(self) -> dict:
        """Return json schema of each stream"""
        return stream_json_schema

    def path(
        self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return ""

    def update_state(self) -> None:
        if self.latest_updated_date:
            if self.latest_updated_date > self.state["updated_at"]:
                self.state = {"updated_at": self.latest_updated_date}
        self.latest_updated_date = None
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_resp = response.json()
        if json_resp["data"]["organizationExportData"] is not None:
            records_str = json_resp["data"]["organizationExportData"]["data"]
            records_obj = json.loads(records_str)
            if self.stream_name in records_obj["data"]:
                records = json.loads(records_str)["data"][f"{self.stream_name}"]
                # more records need to be fetched
                if len(records) == (self.pagination_limit + 1):
                    self.offset += 1
                    return {"offset": self.offset, "limit": self.pagination_limit}

        self.update_state()

        return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"authorization": self.credentials["access_token"], "Content-Type": "application/json"}

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping:
        query = (
            "query organizationExportData($filter: ExportFilter) { organizationExportData(filter: $filter) {data errors { key message } } }"
        )

        filter_obj = {
            "startTime": self.state["updated_at"],
            "offset": self.offset,
            "limit": self.pagination_limit,
            "tables": [self.stream_name],
        }

        if next_page_token is not None:
            filter_obj["offset"] = next_page_token["offset"]
            filter_obj["limit"] = next_page_token["limit"]

        return {"query": query, "variables": {"filter": filter_obj}}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_resp = response.json()
        if json_resp["data"]["organizationExportData"] is not None:
            records_str = json_resp["data"]["organizationExportData"]["data"]
            records_obj = json.loads(records_str)
            yield from records_obj["data"][self.stream_name]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[StreamData]:
        records = super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

        for record in records:
            if len(record["updated_at"]) == 19:
                record["updated_at"] = record["updated_at"] + "Z"
            else:
                record["updated_at"] = datetime.strptime(record["updated_at"], "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%dT%H:%M:%SZ")

            if self.latest_updated_date:
                if record["updated_at"] > self.latest_updated_date:
                    self.latest_updated_date = record["updated_at"]
            else:
                self.latest_updated_date = record["updated_at"]
            retval = {}
            retval["id"] = record["id"]
            retval["updated_at"] = record["updated_at"]
            retval["data"] = record
            yield retval


class IncrementalGlificStream(GlificStream, IncrementalMixin, ABC):
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        return "updated_at"

    @property
    def state(self) -> Mapping[str, Any]:
        if self.cursor_value:
            return {self.cursor_field: self.cursor_value}
        else:
            return {self.cursor_field: self.start_time}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self.cursor_value = value.get(self.cursor_field)
        self._state = value


# Source
class SourceGlific(AbstractSource):
    """Glific source"""

    PAGINATION_LIMIT = 500

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        if "phone" not in config:
            logger.info("Phone number missing")
            return False, "Phone number missing"

        if "password" not in config:
            logger.info("Password missing")
            return False, "Password missing"

        api_url = config["glific_url"]

        endpoint = f"{api_url}/v1/session"
        auth_payload = {"user": {"phone": config["phone"], "password": config["password"]}}

        response = requests.post(endpoint, json=auth_payload, timeout=30)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.info(err)
            return False, response.error.message

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        api_url = config["glific_url"]

        # authenticate and get the credentials for all streams
        endpoint = f"{api_url}/v1/session"
        auth_payload = {"user": {"phone": config["phone"], "password": config["password"]}}
        try:
            response = requests.post(endpoint, json=auth_payload, timeout=30)
            response.raise_for_status()
            credentials = response.json()["data"]
        except requests.exceptions.HTTPError:
            # return empty zero streams since authentication failed
            return []

        # fetch the export config for organization/client/user
        endpoint = api_url
        headers = {"authorization": credentials["access_token"]}

        try:
            query = "query organizationExportConfig { organizationExportConfig { data errors { key message } } }"
            variables = {}
            payload = {"query": query, "variables": variables}

            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.HTTPError:
            # return empty zero streams since config could not be fetched
            return []

        # construct streams
        export_config = json.loads(data["data"]["organizationExportConfig"]["data"])
        streams = []
        for table in export_config["tables"]:
            stream_obj = IncrementalGlificStream(table, api_url, self.PAGINATION_LIMIT, credentials, config)
            streams.append(stream_obj)

        return streams
