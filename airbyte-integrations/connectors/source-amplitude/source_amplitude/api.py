#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import gzip
import io
import json
import urllib.parse as urlparse
import zipfile
from abc import ABC, abstractmethod
from typing import IO, Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib.parse import parse_qs

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class AmplitudeStream(HttpStream, ABC):

    url_base = "https://amplitude.com/api"
    api_version = 2

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        respose_data = response.json()
        yield from respose_data.get(self.name, [])

    def path(self, **kwargs) -> str:
        return f"/{self.api_version}/{self.name}"


class Cohorts(AmplitudeStream):
    primary_key = "id"
    api_version = 3


class Annotations(AmplitudeStream):
    primary_key = "id"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        respose_data = response.json()
        yield from respose_data.get("data", [])


class IncrementalAmplitudeStream(AmplitudeStream, ABC):
    state_checkpoint_interval = 10
    base_params = {}
    cursor_field = "date"
    date_template = "%Y%m%d"

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.parse(start_date)

    @property
    @abstractmethod
    def time_interval(self) -> dict:
        """
        Defining the time interval to determine the difference between the end date and the start date.
        """
        pass

    def _get_end_date(self, current_date: pendulum, end_date: pendulum = pendulum.now()):
        if current_date.add(**self.time_interval).date() < end_date.date():
            end_date = current_date.add(**self.time_interval)
        return end_date

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        parsed = urlparse.urlparse(response.url)
        end = parse_qs(parsed.query).get("end", None)
        if end:
            end_time = pendulum.parse(end[0])
            now = pendulum.now()
            if end_time.date() < now.date():
                return {"start": end[0], "end": self._get_end_date(end_time).strftime(self.date_template)}
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = self.base_params
        if next_page_token:
            params.update(next_page_token)
        else:
            start_datetime = self._start_date
            if stream_state.get(self.cursor_field):
                start_datetime = pendulum.parse(stream_state[self.cursor_field])

            params.update(
                {
                    "start": start_datetime.strftime(self.date_template),
                    "end": self._get_end_date(start_datetime).strftime(self.date_template),
                }
            )
        return params


class Events(IncrementalAmplitudeStream):
    cursor_field = "event_time"
    date_template = "%Y%m%dT%H"
    primary_key = "uuid"
    state_checkpoint_interval = 1000
    time_interval = {"days": 3}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        for gzip_filename in zip_file.namelist():
            with zip_file.open(gzip_filename) as file:
                yield from self._parse_zip_file(file)

    def _parse_zip_file(self, zip_file: IO[bytes]) -> Iterable[Mapping]:
        with gzip.open(zip_file) as file:
            for record in file:
                yield json.loads(record)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=None)

        # API returns data only when requested with a difference between 'start' and 'end' of 6 or more hours.
        if pendulum.parse(params["start"]).add(hours=6) > pendulum.parse(params["end"]):
            return []
        yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        if stream_state or next_page_token:
            params["start"] = pendulum.parse(params["start"]).add(hours=1).strftime(self.date_template)
        return params

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"/{self.api_version}/export"


class ActiveUsers(IncrementalAmplitudeStream):
    base_params = {"m": "active", "i": 1, "g": "country"}
    name = "active_users"
    primary_key = "date"
    time_interval = {"months": 1}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json().get("data", [])
        if response_data:
            series = list(map(list, zip(*response_data["series"])))
            for i, date in enumerate(response_data["xValues"]):
                yield {"date": date, "statistics": dict(zip(response_data["seriesLabels"], series[i]))}

    def path(self, **kwargs) -> str:
        return f"/{self.api_version}/users"


class AverageSessionLength(IncrementalAmplitudeStream):
    name = "average_session_length"
    primary_key = "date"
    time_interval = {"days": 15}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json().get("data", [])
        if response_data:
            # From the Amplitude documentation it follows that "series" is an array with one element which is itself
            # an array that contains the average session length for each day.
            # https://developers.amplitude.com/docs/dashboard-rest-api#returns-2
            series = response_data["series"][0]
            for i, date in enumerate(response_data["xValues"]):
                yield {"date": date, "length": series[i]}

    def path(self, **kwargs) -> str:
        return f"/{self.api_version}/sessions/average"
