import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, Mapping, Optional, Union, List, Dict

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_protocol.models import SyncMode


# Basic full refresh stream
class MintegralStream(HttpStream, ABC):
    page_size = 50
    url_base = "https://ss-api.mintegral.com/api/open/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()["data"]
        if response_json["limit"] * response_json["page"] < response_json["total"]:
            return {"limit": self.page_size, "ext_fields": "creatives", "page": response_json["page"] + 1}
        return None

    def request_params(
            self,
            stream_state: Optional[Mapping[str, Any]],
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ):
        if next_page_token:
            return next_page_token
        else:
            return {
                "limit": self.page_size,
                "ext_fields": "creatives"
            }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.text == "":
            return '{}'
        yield from response.json()["data"]["list"]


class Offers(MintegralStream):
    primary_key = "campaign_id"

    def path(self, **kwargs) -> str:
        return "offers"


class Campaigns(MintegralStream):
    primary_key = "campaign_id"

    def path(self, **kwargs) -> str:
        return "campaign"


class MintegralReportingStream(HttpStream, IncrementalMixin):
    page_size = 500
    backfill_days = 2
    url_base = "https://ss-api.mintegral.com/api/v1/reports/data"

    def __init__(self, authenticator: TokenAuthenticator, **kwargs):
        self._state = {}
        super().__init__(authenticator=authenticator)

    def log(self, message):
        print(message)  # oddly enough logger.debug() os not printed in airbyte logs, but prints are

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "date"

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state[self.cursor_field] = value[self.cursor_field]

    def next_page_token(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        response_json = response.json()
        current_page = int(response_json["page"])
        if current_page < int(response_json["page_count"]):
            return {"page": current_page + 1}
        return None

    def request_params(
            self,
            stream_state: Optional[Mapping[str, Any]],
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ):
        request_params = {
            "start_date": stream_slice[self.cursor_field],
            "end_date": stream_slice[self.cursor_field],
            "per_page": self.page_size,
            "utc": "+0",
            "page": next_page_token["page"] if next_page_token else 1
        }
        self.log(f"Request params: {request_params}")
        return request_params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Dict]:
        if response.text:
            response_json = response.json()
            self.log(f"Page {response_json['page']}, per_page {response_json['per_page']}, "
                     f"page_count {response_json['page_count']}, total_count {response_json['total_count']}")
            yield from response_json["data"]
        else:
            yield {}

    def stream_slices(
            self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        end_date = datetime.now()
        state_date = end_date
        if sync_mode == SyncMode.incremental:
            if self.state and self.state.get(self.cursor_field):
                state_date = datetime.strptime(self.state[self.cursor_field], '%Y-%m-%dT%H:%M:%S.%f')

            self.state = {self.cursor_field: end_date}

        start_date = state_date - timedelta(days=self.backfill_days)

        num_days = (end_date - start_date).days
        dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_days + 1)]

        self.log(f"Slices: {str(dates)}")
        for date in dates:
            yield {self.cursor_field: date}


class Reports(MintegralReportingStream):
    primary_key = ["uuid", "date"]

    def path(self, **kwargs) -> str:
        return ""
