#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog, AirbyteStream
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


# Basic full refresh stream
class AirtableStream(HttpStream, ABC):
    url_base = "https://api.airtable.com/v0/"
    primary_key = "id"

    def __init__(self, base_id: str, table_name: str, schema, **kwargs):
        super().__init__(**kwargs)
        self.base_id = base_id
        self.table_name = table_name
        self.schema = schema

    @property
    def name(self):
        return self.table_name

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.schema

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json()
        offset = json_response.get("offset", None)
        if offset:
            return {"offset": offset}
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return next_page_token
        return {}

    def process_records(self, records):
        processed_records = []
        for record in records:
            processed_record = {
                "_airtable_id": record.get("id"),
                "_airtable_created_time": record.get("createdTime"),
            }
            data = record.get("fields", {})
            # Convert all values to string
            data = {key: str(value) for key, value in data.items()}
            processed_record.update(data)
            processed_records.append(processed_record)
        return processed_records

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get("records", [])
        records = self.process_records(records)
        yield from records

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.base_id}/{self.table_name}"


# Source
class SourceAirtable(AbstractSource):
    schemas = {}

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = TokenAuthenticator(token=config["api_key"]).get_auth_header()
        for table in config["tables"]:
            url = f"https://api.airtable.com/v0/{config['base_id']}/{table}?pageSize=1"
            try:
                response = requests.get(url, headers=auth)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                return False, e
        return True, None

    def discover(self, logger: AirbyteLogger, config) -> AirbyteCatalog:
        streams = []
        auth = TokenAuthenticator(token=config["api_key"]).get_auth_header()
        for table in config["tables"]:
            url = f"https://api.airtable.com/v0/{config['base_id']}/{table}?pageSize=1"
            response = requests.get(url, headers=auth)
            response.raise_for_status()
            record = response.json().get("records", [])[0].get("fields", {})
            properties = {
                "_airtable_id": {"type": ["null", "string"]},
                "_airtable_created_time": {"type": ["null", "string"]},
            }

            for field in record:
                properties[field] = {"type": ["null", "string"]}
                json_schema = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": properties,
                }

            self.schemas[table] = json_schema
            streams.append(
                AirbyteStream(
                    name=table,
                    json_schema=json_schema,
                    supported_sync_modes=[SyncMode.full_refresh],
                    supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append_dedup],
                )
            )
        return AirbyteCatalog(streams=streams)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["api_key"])
        streams = []
        for table_name in config["tables"]:
            kwargs = {"base_id": config["base_id"], "table_name": table_name, "authenticator": auth, "schema": self.schemas.get(table_name)}
            stream = AirtableStream(**kwargs)
            streams.append(stream)
        return streams
