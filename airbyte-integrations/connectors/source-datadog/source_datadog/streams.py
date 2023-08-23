#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from dateutil.parser import parse
from pydantic.datetime_parse import timedelta


class DatadogStream(HttpStream, ABC):
    """
    Datadog API Reference: https://docs.datadoghq.com/api/latest/
    """

    primary_key: Optional[str] = None
    parse_response_root: Optional[str] = None

    def __init__(
        self,
        site: str,
        query: str,
        max_records_per_request: int,
        start_date: str,
        end_date: str,
        query_start_date: str,
        query_end_date: str,
        queries: List[Dict[str, str]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.site = site
        self.query = query
        self.max_records_per_request = max_records_per_request
        self.start_date = start_date
        self.end_date = end_date
        self.query_start_date = query_start_date
        self.query_end_date = query_end_date
        self.queries = queries or []
        self._cursor_value = None

    @property
    def url_base(self) -> str:
        return f"https://api.{self.site}/api"

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params: Dict[str, str] = {}

        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json if not self.parse_response_root else response_json.get(self.parse_response_root, [])
        for record in records:
            yield self.transform(record=record, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return record


class V1ApiDatadogStream(DatadogStream, ABC):
    @property
    def url_base(self) -> str:
        return f"{super().url_base}/v1/"

    @property
    def http_method(self) -> str:
        return "GET"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class Dashboards(V1ApiDatadogStream):
    """
    https://docs.datadoghq.com/api/latest/dashboards/#get-all-dashboards
    """

    parse_response_root: Optional[str] = "dashboards"

    def path(self, **kwargs) -> str:
        return "dashboard"


class Downtimes(V1ApiDatadogStream):
    """
    https://docs.datadoghq.com/api/latest/downtimes/#get-all-downtimes
    """

    def path(self, **kwargs) -> str:
        return "downtime"


class SyntheticTests(V1ApiDatadogStream):
    """
    https://docs.datadoghq.com/api/latest/synthetics/#get-the-list-of-all-tests
    """

    parse_response_root: Optional[str] = "tests"

    def path(self, **kwargs) -> str:
        return "synthetics/tests"


class V2ApiDatadogStream(DatadogStream, ABC):
    @property
    def url_base(self) -> str:
        return f"{super().url_base}/v2/"


class IncrementalSearchableStream(V2ApiDatadogStream, IncrementalMixin, ABC):
    primary_key: Optional[str] = "id"
    parse_response_root: Optional[str] = "data"

    def __init__(self, site: str, query: str, max_records_per_request: int, start_date: str, end_date: str, **kwargs):
        super().__init__(site, query, max_records_per_request, start_date, end_date, **kwargs)
        self._cursor_value = ""

    @property
    def http_method(self) -> str:
        return "POST"

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: self.start_date}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "sync_date"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        cursor = None
        if next_page_token:
            cursor = next_page_token.get("page", {}).get("cursor", {})
        return self.get_payload(cursor)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        cursor = response_json.get("meta", {}).get("page", {}).get("after", {})
        if not cursor:
            self._cursor_value = self.end_date
        else:
            return self.get_payload(cursor)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record[self.cursor_field] = self._cursor_value if self._cursor_value else self.end_date
        return record

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if self.start_date >= self.end_date or self.end_date <= self._cursor_value:
            return []
        return super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

    def get_payload(self, cursor: Optional[str]) -> Mapping[str, Any]:
        payload = {
            "filter": {"query": self.query, "from": self._cursor_value if self._cursor_value else self.start_date, "to": self.end_date},
            "page": {"limit": self.max_records_per_request},
        }
        if cursor:
            payload["page"]["cursor"] = cursor

        return payload


class AuditLogs(IncrementalSearchableStream):
    """
    https://docs.datadoghq.com/api/latest/audit/#search-audit-logs-events
    """

    def path(self, **kwargs) -> str:
        return "audit/events/search"


class Logs(IncrementalSearchableStream):
    """
    https://docs.datadoghq.com/api/latest/logs/#search-logs
    """

    def path(self, **kwargs) -> str:
        return "logs/events/search"


class BasedListStream(V2ApiDatadogStream, ABC):
    parse_response_root: Optional[str] = "data"

    @property
    def http_method(self) -> str:
        return "GET"


class Metrics(BasedListStream):
    """
    https://docs.datadoghq.com/api/latest/metrics/#get-a-list-of-metrics
    """

    def path(self, **kwargs) -> str:
        return "metrics?window[seconds]=1209600"  # max value allowed (2 weeks)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class PaginatedBasedListStream(BasedListStream, ABC):
    primary_key: Optional[str] = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        offset = None
        if next_page_token:
            offset = next_page_token.get("offset")
        return self.get_url_path(offset)

    @abstractmethod
    def get_url_path(self, offset: Optional[str]) -> str:
        """
        Returns the relative URL with the corresponding offset
        """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        next_offset = response_json.get("meta", {}).get("pagination", {}).get("next_offset", -1)
        current_offset = response_json.get("meta", {}).get("pagination", {}).get("offset", -1)
        next_page_token = None
        if next_offset != current_offset:
            next_page_token = {"offset": next_offset}
        return next_page_token


class Incidents(PaginatedBasedListStream):
    """
    https://docs.datadoghq.com/api/latest/incidents/#get-a-list-of-incidents
    """

    def get_url_path(self, offset: Optional[str]) -> str:
        params = f"&page[offset]={offset}" if offset else ""
        return f"incidents?page[size]={self.max_records_per_request}{params}"


class IncidentTeams(PaginatedBasedListStream):
    """
    https://docs.datadoghq.com/api/latest/incident-teams/#get-a-list-of-all-incident-teams
    """

    def get_url_path(self, offset: Optional[str]) -> str:
        params = f"&page[offset]={offset}" if offset else ""
        return f"teams?page[size]={self.max_records_per_request}{params}"


class Users(PaginatedBasedListStream):
    """
    https://docs.datadoghq.com/api/latest/users/#list-all-users
    """

    current_page = 0

    def get_url_path(self, offset: Optional[int]) -> str:
        params = f"&page[number]={offset}" if offset else ""
        return f"users?page[size]={self.max_records_per_request}{params}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        next_page_token = None
        if len(response_json.get("data", [])) > 0:
            self.current_page += 1
            next_page_token = {"offset": self.current_page}
        return next_page_token


class SeriesStream(IncrementalSearchableStream, ABC):
    """
    https://docs.datadoghq.com/api/latest/metrics/?code-lang=curl#query-timeseries-data-across-multiple-products
    """

    primary_key: Optional[str] = None
    parse_response_root: Optional[str] = "data"

    def __init__(self, name, data_source, query_string, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.data_source = data_source
        self.query_string = query_string

    @property
    def http_method(self) -> str:
        return "POST"

    def path(self, **kwargs) -> str:
        return "query/timeseries"

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "sync_date"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:

        if self.query_end_date:
            end_date = int(parse(self.query_end_date).timestamp() * 1000)
        else:
            end_date = int(datetime.now().timestamp()) * 1000

        if self.query_start_date:
            start_date = int(parse(self.query_start_date).timestamp() * 1000)
        elif self._cursor_value:
            start_date = int(parse(self._cursor_value).timestamp() * 1000)
        else:
            start_date = int((datetime.now() - timedelta(hours=24)).timestamp()) * 1000

        payload = {
            "data": {
                "type": "timeseries_request",
                "attributes": {
                    "to": end_date,
                    "from": start_date,
                    "queries": [
                        {
                            "data_source": self.data_source,
                            "name": self.name,
                        }
                    ],
                },
            }
        }

        if self.data_source in ["metrics", "cloud_cost"]:
            payload["data"]["attributes"]["queries"][0]["query"] = self.query_string
        elif self.data_source in ["logs", "rum"]:
            payload["data"]["attributes"]["queries"][0]["search"] = {"query": self.query_string}
            payload["data"]["attributes"]["queries"][0]["compute"] = {"aggregation": "count"}
            print(payload)
        return payload

    def get_json_schema(self) -> Mapping[str, Any]:
        local_json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }
        return local_json_schema

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        data["stream"] = self.name
        data["query"] = self.query_string
        data["data_source"] = self.data_source
        return [data]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        self._cursor_value = self.end_date
        return None
