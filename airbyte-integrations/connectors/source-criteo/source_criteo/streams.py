#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import uuid
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

BASE_URL = "https://api.criteo.com"


class CriteoStream(HttpStream, ABC):

    url_base = BASE_URL
    primary_key = "uuid"
    data_field = "Rows"
    DATE_FORMAT = "%Y-%m-%d"
    cursor_field = "Day"

    def __init__(
        self,
        authenticator: Union[HttpAuthenticator, requests.auth.AuthBase],
        advertiserIds: str,
        start_date: str,
        end_date: str,
        dimensions: str,
        metrics: str,
        lookback_window: int,
        currency: str,
        timezone: str,
    ):
        super().__init__(authenticator=authenticator)
        self.advertiserIds = advertiserIds
        self.start_date = start_date
        self.end_date = end_date
        self.dimensions = dimensions
        self.metrics = metrics
        self._cursor_value = None
        self.lookback_window = lookback_window
        self.currency = currency
        self.timezone = timezone

    @property
    def http_method(self) -> str:
        return "POST"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if not self.data_field:
            yield response.json()

        else:
            records = response.json().get(self.data_field) or []
            for record in records:
                yield record


class StatisticReport(CriteoStream, IncrementalMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cursor_value = ""

    @property
    def cursor_field(self) -> str:
        return "Day"

    @staticmethod
    def add_primary_key() -> dict:
        return {"uuid": str(uuid.uuid4())}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {self.cursor_field: self._cursor_value} if self._cursor_value else {}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._cursor_value = value.get(self.cursor_field, self.start_date)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if (datetime.strptime(self.start_date, "%Y-%m-%d") - timedelta(days=self.lookback_window)) > datetime.strptime(
            self.end_date, "%Y-%m-%d"
        ):
            return []
        if self._cursor_value:
            if (datetime.strptime(self._cursor_value, "%Y-%m-%d") - timedelta(days=self.lookback_window)) > datetime.strptime(
                self.end_date, "%Y-%m-%d"
            ):
                return []
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            yield self.add_primary_key() | record
            self._cursor_value = max(record[self.cursor_field], self._cursor_value)

    @property
    def http_method(self) -> str:
        return "POST"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        start_date = (datetime.strptime(self.start_date, "%Y-%m-%d") - timedelta(days=self.lookback_window)).strftime("%Y-%m-%d")
        if self._cursor_value:
            start_date = (datetime.strptime(self._cursor_value, "%Y-%m-%d") - timedelta(days=self.lookback_window)).strftime("%Y-%m-%d")
        return {
            "advertiserIds": self.advertiserIds,
            "startDate": start_date,
            "endDate": self.end_date,
            "format": "json",
            "dimensions": self.dimensions,
            "metrics": self.metrics,
            "timezone": self.timezone,
            "currency": self.currency,
        }

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Override get_json_schema CDK method to retrieve the schema information for Criteo Object dynamically.
        """
        schema: Dict[str, Any] = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": {
                "uuid": {"type": ["string"], "description": "Custom unique identifier for each record, to support primary key"},
            },
        }

        schema["properties"].update({d: {"type": "string"} for d in self.dimensions if d != "Day"})
        schema["properties"].update({"Day": {"type": "string", "format": "date"}})

        for dim in self.dimensions:
            if dim.endswith("Id"):
                schema["properties"].update({dim[:-2]: {"type": "string"}})

        schema["properties"].update({m: {"type": "string"} for m in self.metrics})

        schema["properties"].update({"Currency": {"type": "string"}})
        return schema

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "2023-01/statistics/report"
