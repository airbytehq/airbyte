#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import gzip
import io
import json
import logging
import zipfile
from typing import IO, Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream

LOGGER = logging.getLogger("airbyte")

HTTP_ERROR_CODES = {
    400: {
        "msg": "The file size of the exported data is too large. Shorten the time ranges and try again. The limit size is 4GB.",
        "lvl": "ERROR",
    },
    404: {
        "msg": "No data collected",
        "lvl": "WARN",
    },
    504: {
        "msg": "The amount of data is large causing a timeout. For large amounts of data, the Amazon S3 destination is recommended.",
        "lvl": "ERROR",
    },
}


def error_msg_from_status(status: int = None):
    if status:
        level = HTTP_ERROR_CODES[status]["lvl"]
        message = HTTP_ERROR_CODES[status]["msg"]
        if level == "ERROR":
            LOGGER.error(message)
        elif level == "WARN":
            LOGGER.warning(message)
        else:
            LOGGER.error(f"Unknown error occured: code {status}")


class Events(HttpStream):
    api_version = 2
    base_params = {}
    cursor_field = "server_upload_time"
    date_template = "%Y%m%dT%H"
    compare_date_template = "%Y-%m-%d %H:%M:%S.%f"
    primary_key = "uuid"
    state_checkpoint_interval = 1000

    def __init__(self, data_region: str, start_date: str, event_time_interval: dict = None, **kwargs):
        if event_time_interval is None:
            event_time_interval = {"size_unit": "hours", "size": 24}
        self.data_region = data_region
        self.event_time_interval = event_time_interval
        self._start_date = pendulum.parse(start_date) if isinstance(start_date, str) else start_date
        self.date_time_fields = self._get_date_time_items_from_schema()
        super().__init__(**kwargs)

    @property
    def url_base(self) -> str:
        subdomain = "analytics.eu." if self.data_region == "EU Residency Server" else ""
        return f"https://{subdomain}amplitude.com/api/"

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    @property
    def time_interval(self) -> dict:
        return {self.event_time_interval.get("size_unit"): self.event_time_interval.get("size")}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # save state value in source native format
        if self.compare_date_template:
            latest_state = pendulum.parse(latest_record[self.cursor_field]).strftime(self.compare_date_template)
        else:
            latest_state = latest_record.get(self.cursor_field, "")
        return {self.cursor_field: max(latest_state, current_stream_state.get(self.cursor_field, ""))}

    def _get_date_time_items_from_schema(self):
        """
        Get all properties from schema with format: 'date-time'
        """
        result = []
        schema = self.get_json_schema()
        for key, value in schema["properties"].items():
            if value.get("format") == "date-time":
                result.append(key)
        return result

    def _date_time_to_rfc3339(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Transform 'date-time' items to RFC3339 format
        """
        for item in record:
            if item in self.date_time_fields and record[item]:
                record[item] = pendulum.parse(record[item]).to_rfc3339_string()
        return record

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

    def _parse_zip_file(self, zip_file: IO[bytes]) -> Iterable[MutableMapping]:
        with gzip.open(zip_file) as file:
            for record in file:
                yield json.loads(record)

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        slices = []
        start = pendulum.parse(stream_state.get(self.cursor_field)) if stream_state else self._start_date
        end = pendulum.now()
        if start > end:
            self.logger.info("The data cannot be requested in the future. Skipping stream.")
            return []

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
