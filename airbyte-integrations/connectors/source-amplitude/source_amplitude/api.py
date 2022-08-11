#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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

from .errors import HTTP_ERROR_CODES, error_msg_from_status


class AmplitudeStream(HttpStream, ABC):

    url_base = "https://amplitude.com/api/"
    api_version = 2

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        status = response.status_code
        if status in HTTP_ERROR_CODES.keys():
            error_msg_from_status(status)
            yield from []
        else:
            yield from response.json().get(self.data_field, [])

    def path(self, **kwargs) -> str:
        return f"{self.api_version}/{self.name}"


class Cohorts(AmplitudeStream):
    primary_key = "id"
    api_version = 3
    data_field = "cohorts"


class Annotations(AmplitudeStream):
    primary_key = "id"
    data_field = "data"


class IncrementalAmplitudeStream(AmplitudeStream, ABC):
    state_checkpoint_interval = 10
    base_params = {}
    cursor_field = "date"
    date_template = "%Y%m%d"
    compare_date_template = None

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

    def _get_date_time_items_from_schema(self):
        """
        Get all properties from schema with format: 'date-time'
        """
        result = []
        schema = self.get_json_schema()["properties"]
        for key, value in schema.items():
            if value.get("format") == "date-time":
                result.append(key)
        return result

    def _date_time_to_rfc3339(self, record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Transform 'date-time' items to RFC3339 format
        """
        date_time_fields = self._get_date_time_items_from_schema()
        for item in record:
            if item in date_time_fields:
                record[item] = pendulum.parse(record[item]).to_rfc3339_string()
        return record

    def _get_end_date(self, current_date: pendulum, end_date: pendulum = pendulum.now()):
        if current_date.add(**self.time_interval).date() < end_date.date():
            end_date = current_date.add(**self.time_interval)
        return end_date

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # save state value in source native format
        if self.compare_date_template:
            latest_state = pendulum.parse(latest_record[self.cursor_field]).strftime(self.compare_date_template)
        else:
            latest_state = latest_record[self.cursor_field]
        return {self.cursor_field: max(latest_state, current_stream_state.get(self.cursor_field, ""))}

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
    compare_date_template = "%Y-%m-%d %H:%M:%S.%f"
    primary_key = "uuid"
    state_checkpoint_interval = 1000
    time_interval = {"days": 1}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        state_value = stream_state[self.cursor_field] if stream_state else self._start_date.strftime(self.compare_date_template)
        try:
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        except zipfile.BadZipFile as e:
            self.logger.exception(e)
            self.logger.error(
                f"Received an invalid zip file in response to URL: {response.request.url}."
                f"The size of the response body is: {len(response.content)}"
            )
            return []

        for gzip_filename in zip_file.namelist():
            with zip_file.open(gzip_filename) as file:
                for record in self._parse_zip_file(file):
                    if record[self.cursor_field] >= state_value:
                        yield self._date_time_to_rfc3339(record)  # transform all `date-time` to RFC3339

    def _parse_zip_file(self, zip_file: IO[bytes]) -> Iterable[Mapping]:
        with gzip.open(zip_file) as file:
            for record in file:
                yield json.loads(record)

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        slices = []
        start = pendulum.parse(stream_state.get(self.cursor_field)) if stream_state else self._start_date
        end = pendulum.now()
        while start <= end:
            slices.append(
                {
                    "start": start.strftime(self.date_template),
                    "end": start.add(**self.time_interval).subtract(hours=1).strftime(self.date_template),
                }
            )
            start = start.add(**self.time_interval)
        return slices

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        start = pendulum.parse(stream_slice["start"])
        end = pendulum.parse(stream_slice["end"])
        if start > end:
            yield from []
        # sometimes the API throws a 404 error for not obvious reasons, we have to handle it and log it.
        # for example, if there is no data from the specified time period, a 404 exception is thrown
        # https://developers.amplitude.com/docs/export-api#status-codes
        try:
            self.logger.info(f"Fetching {self.name} time range: {start.strftime('%Y-%m-%dT%H')} - {end.strftime('%Y-%m-%dT%H')}")
            records = super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
            yield from records
        except requests.exceptions.HTTPError as error:
            status = error.response.status_code
            if status in HTTP_ERROR_CODES.keys():
                error_msg_from_status(status)
                yield from []
            else:
                self.logger.error(f"Error during syncing {self.name} stream - {error}")
                raise

    def request_params(self, stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = self.base_params
        params["start"] = pendulum.parse(stream_slice["start"]).strftime(self.date_template)
        params["end"] = pendulum.parse(stream_slice["end"]).strftime(self.date_template)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, **kwargs) -> str:
        return f"{self.api_version}/export"


class ActiveUsers(IncrementalAmplitudeStream):
    base_params = {"m": "active", "i": 1, "g": "country"}
    name = "active_users"
    primary_key = "date"
    time_interval = {"months": 1}
    data_field = "data"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json().get(self.data_field, [])
        if response_data:
            series = list(map(list, zip(*response_data["series"])))
            for i, date in enumerate(response_data["xValues"]):
                yield {"date": date, "statistics": dict(zip(response_data["seriesLabels"], series[i]))}

    def path(self, **kwargs) -> str:
        return f"{self.api_version}/users"


class AverageSessionLength(IncrementalAmplitudeStream):
    name = "average_session_length"
    primary_key = "date"
    time_interval = {"days": 15}
    data_field = "data"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json().get(self.data_field, [])
        if response_data:
            # From the Amplitude documentation it follows that "series" is an array with one element which is itself
            # an array that contains the average session length for each day.
            # https://developers.amplitude.com/docs/dashboard-rest-api#returns-2
            series = response_data["series"][0]
            for i, date in enumerate(response_data["xValues"]):
                yield {"date": date, "length": series[i]}

    def path(self, **kwargs) -> str:
        return f"{self.api_version}/sessions/average"
