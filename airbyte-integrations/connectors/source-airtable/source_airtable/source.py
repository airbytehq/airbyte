#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

from .helpers import Helpers


# Basic full refresh stream
class AirtableStream(HttpStream, ABC):
    url_base = "https://api.airtable.com/v0/"
    primary_key = "id"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

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
        for record in records:
            data = record.get("fields", {})
            processed_record = {"_airtable_id": record.get("id"), "_airtable_created_time": record.get("createdTime"), **data}
            yield processed_record

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
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = TokenAuthenticator(token=config["api_key"])
        for table in config["tables"]:
            try:
                Helpers.get_first_row(auth, config["base_id"], table)
            except Exception as e:
                return False, str(e)
        return True, None

    def discover(self, logger: AirbyteLogger, config) -> AirbyteCatalog:
        streams = []
        auth = TokenAuthenticator(token=config["api_key"])
        for table in config["tables"]:
            record = Helpers.get_first_row(auth, config["base_id"], table)
            json_schema = Helpers.get_json_schema(record)
            airbyte_stream = Helpers.get_airbyte_stream(table, json_schema)
            streams.append(airbyte_stream)
        return AirbyteCatalog(streams=streams)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["api_key"])
        streams = []
        for table in config["tables"]:
            record = Helpers.get_first_row(auth, config["base_id"], table)
            json_schema = Helpers.get_json_schema(record)
            stream = AirtableStream(base_id=config["base_id"], table_name=table, authenticator=auth, schema=json_schema)
            streams.append(stream)
        return streams
