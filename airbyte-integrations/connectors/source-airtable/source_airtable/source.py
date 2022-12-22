#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
import logging
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


URL_BASE: str = "https://api.airtable.com/v0/"


class AirtableBases(HttpStream):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    url_base = URL_BASE
    primary_key = None
    name = "bases"
    raise_on_http_errors = True
        
    def path(self, **kwargs) -> str:
        """
        Documentation: https://airtable.com/developers/web/api/list-bases
        """
        return "meta/bases"
    
    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 403 or response.status_code == 422:
            self.logger.error(f"Stream {self.name}: permission denied or entity is unprocessable. Skipping.")
            setattr(self, "raise_on_http_errors", False)
            return False
        return super().should_retry(response)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Based on official docs: https://airtable.com/developers/web/api/rate-limits
        when 429 is received, we should wait at least 30 sec.
        """
        if response.status_code == 429:
            self.logger.error(f"Stream {self.name}: rate limit exceeded")
            return 30.0
    
    def next_page_token(self, response: requests.Response, **kwargs) -> str:
        """
        The bases list could be more than 100 records, therefore the pagination is required to fetch all of them.
        """
        next_page = response.json().get("offset")
        if next_page:
            return {"offset": next_page}
        return None
    
    def request_params(self, next_page_token: str = None, **kwargs) -> Mapping[str, Any]:
        params = {}
        if next_page_token:
            params["offset"] = next_page_token
        return params
    
    def parse_response(self, response: requests.Response, **kwargs) -> Mapping[str, Any]:
        """
        Example output: 
            {
                'bases': [
                    {'id': '_some_id_', 'name': 'users', 'permissionLevel': 'create'}, 
                    {'id': '_some_id_', 'name': 'Test Base', 'permissionLevel': 'create'},
                ]
            }
        """
        records = response.json().get(self.name)
        yield from records


class AirtableTables(AirtableBases):
    
    def __init__(self, base_id: list, **kwargs):
        super().__init__(**kwargs)
        self.base_id = base_id
        
    name = "tables"
    
    def path(self, **kwargs) -> str:
        """
        Documentation: https://airtable.com/developers/web/api/list-bases
        """
        return f"{super().path()}/{self.base_id}/tables"


class AirtableStream(HttpStream, ABC):
    
    def __init__(self, stream_path: str, stream_name: str, stream_schema, **kwargs):
        super().__init__(**kwargs)
        self.stream_path = stream_path
        self.stream_name = stream_name
        self.stream_schema = stream_schema
        
    url_base = URL_BASE
    primary_key = "id"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    raise_on_http_errors = True    
    
    @property
    def name(self):
        return self.stream_name
    
    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 403 or response.status_code == 422:
            self.logger.error(f"Stream {self.name}: permission denied or entity is unprocessable. Skipping.")
            setattr(self, "raise_on_http_errors", False)
            return False
        return super().should_retry(response)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Based on official docs: https://airtable.com/developers/web/api/rate-limits
        when 429 is received, we should wait at least 30 sec.
        """
        if response.status_code == 429:
            self.logger.error(f"Stream {self.name}: rate limit exceeded")
            return 30.0

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.stream_schema

    def next_page_token(self, response: requests.Response, **kwargs) -> Optional[Mapping[str, Any]]:
        next_page = response.json().get("offset")
        if next_page:
            return {"offset": next_page}
        return None

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        """
        All available params: https://airtable.com/developers/web/api/list-records#query
        """
        if next_page_token:
            return next_page_token
        return {}

    def process_records(self, records) -> Iterable[Mapping[str, Any]]:
        for record in records:
            data = record.get("fields")
            if len(data) > 0:
                yield {
                    "_airtable_id": record.get("id"), 
                    "_airtable_created_time": record.get("createdTime"), 
                    **data,
                }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get("records", [])
        yield from self.process_records(records)

    def path(self, **kwargs) -> str:
        return self.stream_path


class SourceAirtable(AbstractSource):
    
    logger: logging.Logger = logging.getLogger("airbyte")
    
    prepared_catalog: List[AirbyteCatalog] = []
    
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        auth = TokenAuthenticator(token=config["api_key"])
        try:        
            # try reading first table from each base, to check the connectivity
            for base in AirtableBases(authenticator=auth).read_records(sync_mode=None):
                base_id = base.get("id")
                base_name = base.get("name")
                self.logger.info(f"Reading first table info for base: {base_name}")
                next(AirtableTables(base_id=base_id, authenticator=auth).read_records(sync_mode=None))
            return True, None
        except Exception as e:
            return False, str(e) 

    def discover(self, logger: AirbyteLogger, config) -> AirbyteCatalog:
        """
        Override to provide the dynamic schema generation capabilities,
        using resource available for authenticated user.
        
        Retrieve: Bases, Tables from each Base, generate JSON Schema for each table.
        """
        auth = TokenAuthenticator(token=config["api_key"])
        # tables placeholder
        tables: Mapping[str, List] = {}
        # list all bases available for authenticated account
        for base in AirtableBases(authenticator=auth).read_records(sync_mode=None):
            base_id = base.get("id")
            base_name = Helpers.clean_name(base.get("name"))
            # list and process each table under each base to generate the JSON Schema
            tables[base_id] = list(AirtableTables(base_id=base_id, authenticator=auth).read_records(sync_mode=None))
            for table in tables[base_id]:
                table_id = table.get("id")
                table_name = Helpers.clean_name(table.get("name"))
                stream_name = f"{base_name}/{table_name}"
                self.prepared_catalog.append(
                    {
                        "stream_path": f"{base_id}/{table_id}",
                        "catalog": Helpers.get_airbyte_stream(stream_name, Helpers.get_json_schema(table)),
                    }
                )
        # generate catalog
        return AirbyteCatalog(streams=[catalog["catalog"] for catalog in self.prepared_catalog])
    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["api_key"])
        # streams placeholder
        streams_list: List[Stream] = []
        # get prepared catalog for ruther stream generation
        self.discover(logger=None, config=config)
        for stream in self.prepared_catalog:
            streams_list.append(
                AirtableStream(
                    stream_path=stream["stream_path"],
                    stream_name=stream["catalog"].name,
                    stream_schema=stream["catalog"].json_schema,
                    authenticator=auth,
                )
            )
        return streams_list
