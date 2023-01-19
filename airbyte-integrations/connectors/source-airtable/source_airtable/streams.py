#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_airtable.schema_helpers import SchemaHelpers

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
            return next_page
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
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.stream_schema

    def next_page_token(self, response: requests.Response, **kwargs) -> Optional[Mapping[str, Any]]:
        next_page = response.json().get("offset")
        if next_page:
            return next_page
        return None

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        """
        All available params: https://airtable.com/developers/web/api/list-records#query
        """
        params = {}
        if next_page_token:
            params["offset"] = next_page_token
        return params

    def process_records(self, records) -> Iterable[Mapping[str, Any]]:
        for record in records:
            data = record.get("fields")
            if len(data) > 0:
                yield {
                    "_airtable_id": record.get("id"),
                    "_airtable_created_time": record.get("createdTime"),
                    **{SchemaHelpers.clean_name(k): v for k, v in data.items()},
                }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get("records", [])
        yield from self.process_records(records)

    def path(self, **kwargs) -> str:
        return self.stream_path
