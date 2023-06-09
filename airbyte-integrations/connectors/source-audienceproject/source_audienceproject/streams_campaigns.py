#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin

from .streams import IncrementalAudienceprojectStream


class Campaigns(IncrementalAudienceprojectStream, IncrementalMixin):
    primary_key = "id"
    max_records = 100
    cursor_field = "created"
    start = 0

    def __init__(self, authenticator, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()
        self._cursor_value = ""
        self.stream_end = ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Start indicates, start index of the campaigns batch with Default value is 0.
        # max_records count of max object in a response indicating total number of campaigns that can be returned.
        # total count indicates total data objects in all pages.
        # All pages are checked even if fetched records are less than total_count that can be fetched.
        total_count = response.json().get("meta").get("totalCount")
        self.start += self.max_records
        if self.start < total_count:
            return {"start": self.start, "maxResults": self.max_records}
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        self.stream_end = self.config.get("end_date")
        params = {"reportStart": stream_start, "reportEnd": stream_end, "sortDirection": "asc"}
        if self.config.get("campaign_status"):
            params.update({"status": self.config.get("campaign_status")})
        if next_page_token:
            params.update(**next_page_token)
        return params

    @property
    def use_cache(self) -> bool:
        return True

    @property
    def cache_filename(self):
        return "campaigns.yml"

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        self.sync_mode = kwargs.get("sync_mode", SyncMode.incremental)
        for record in super().read_records(*args, **kwargs):
            if self.state:
                if self._cursor_value < self.stream_end:
                    self.state = {self.cursor_field: max(record.get(self.cursor_field, ""), self.state.get(self.cursor_field, ""))}
                    if record[self.cursor_field] >= self.state.get(self.cursor_field):
                        yield record
            else:
                self._cursor_value = record.get("created")
                self.state = {self.cursor_field: self._cursor_value}
                yield from record

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        resp = response.json()
        if resp:
            for objects in resp.get("data"):
                objects.update({"created": objects.get("dates").get("created")})
                yield objects

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "campaigns"
