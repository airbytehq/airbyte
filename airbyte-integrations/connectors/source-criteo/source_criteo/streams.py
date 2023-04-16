#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import uuid
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, Mapping, Optional, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

BASE_URL = "https://api.criteo.com"


class CriteoStream(HttpStream, ABC):

    url_base = BASE_URL
    primary_key = "uuid"
    data_field = "Rows"
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
        self._start_date = start_date
        self._end_date = end_date
        self.dimensions = dimensions
        self.metrics = metrics
        self._cursor_value = None
        self.lookback_window = lookback_window
        self.currency = currency
        self.timezone = timezone

    @property
    def http_method(self) -> str:
        return "POST"

    @staticmethod
    def add_primary_key() -> dict:
        return {"uuid": str(uuid.uuid4())}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if not self.data_field:
            yield response.json()

        else:
            records = response.json().get(self.data_field) or []
            for record in records:
                yield record


class Analytics(CriteoStream):
    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.strftime("%Y-%m-%d")}
        else:
            return {self.cursor_field: self._start_date[:10]}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], "%Y-%m-%d")

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            if self._cursor_value:
                latest_record_date = datetime.strptime(record[self.cursor_field], "%Y-%m-%d")
                self._cursor_value = max(self._cursor_value, latest_record_date)
            yield record

    @property
    def http_method(self) -> str:
        return "POST"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        start_date = (datetime.strptime(self._start_date, "%Y-%m-%dT%H:%M:%SZ") - timedelta(days=30)).strftime("%Y-%m-%d")
        if self._cursor_value:
            start_date = (self._cursor_value - timedelta(days=self.lookback_window)).strftime("%Y-%m-%d")
        return {
            "advertiserIds": self.advertiserIds,
            "startDate": start_date,
            "endDate": self._end_date,
            "format": "json",
            "dimensions": self.dimensions,
            "metrics": self.metrics,
            "timezone": self.timezone,
            "currency": self.currency,
        }

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Override get_json_schema CDK method to retrieve the schema information for GoogleAnalyticsV4 Object dynamically.
        """
        schema: Dict[str, Any] = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "properties": {
                "property_id": {"type": ["string"]},
                "uuid": {"type": ["string"], "description": "Custom unique identifier for each record, to support primary key"},
            },
        }

        schema["properties"].update({d: {"type": "string"} for d in self.dimensions})

        schema["properties"].update({m: {"type": "number"} for m in self.metrics})

        return schema

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "2023-01/statistics/report"
