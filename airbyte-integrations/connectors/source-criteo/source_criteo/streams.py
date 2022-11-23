from abc import ABC
from typing import Any, Iterable, Mapping, Optional, Union, MutableMapping
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

BASE_URL = "https://api.criteo.com"

class CriteoStream(HttpStream, ABC):

    url_base = BASE_URL
    primary_key = None
    data_field = "Rows"

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

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        next_page = decoded_response.get("nextPageToken")
        if next_page:
            return {"pageToken": next_page}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        if next_page_token:
            params = next_page_token
            return params
        else:
            return {}


    @property
    def http_method(self) -> str:
        return "POST"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if not self.data_field:
            yield response.json()

        else:
            records = response.json().get(self.data_field) or []
            for record in records:
                yield record

class Adset(CriteoStream):

    @property
    def http_method(self) -> str:
        return "POST"

    def request_body_json(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return  {
            "advertiserIds": self.advertiserIds,
            "startDate": self._start_date,
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
