from abc import ABC
from typing import Any, Iterable, Mapping, Optional, Union, MutableMapping
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from datetime import datetime, timedelta, date

BASE_URL = "https://api.criteo.com"

class CriteoStream(HttpStream, ABC):

    url_base = BASE_URL
    primary_key = None
    data_field = "Rows"
    cursor_field = "Day"

    def __init__(
        self,
        authenticator: Union[HttpAuthenticator, requests.auth.AuthBase],
        advertiserIds: str,
        start_date: str,
        end_date: str,
        dimensions: str,
        metrics: str
    ):
        super().__init__(authenticator=authenticator)
        self.advertiserIds = advertiserIds
        self._start_date = start_date
        self._end_date = end_date
        self.dimensions = dimensions
        self.metrics = metrics
        self._cursor_value = None

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

class Analytics(CriteoStream):

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.strftime('%Y-%m-%d')}
        else:
            return {self.cursor_field: self._start_date[:10]}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], '%Y-%m-%d')

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            if self._cursor_value:
                latest_record_date = datetime.strptime(record[self.cursor_field], '%Y-%m-%d')
                self._cursor_value = max(self._cursor_value, latest_record_date)
            yield record

    @property
    def http_method(self) -> str:
        return "POST"

    def request_body_json(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        start_date = self._start_date
        if self._cursor_value:
            start_date = (self._cursor_value - timedelta(days=30)).strftime('%Y-%m-%d')
        return  {
            "advertiserIds": self.advertiserIds,
            "startDate": start_date,
            "endDate": self._end_date,
            "format": "json",
            "dimensions": self.dimensions.split(','),
            "metrics": self.metrics.split(','),
            "timezone": "Europe/Rome",
            "currency": "EUR"
        }

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "2022-01/statistics/report"
