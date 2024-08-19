#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import gzip
import io
import json
import logging
import zipfile
from typing import IO, Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import CheckpointMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, FailureType, ResponseAction

LOGGER = logging.getLogger("airbyte")


class Events(HttpStream, CheckpointMixin):
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
        if not hasattr(self, "_state"):
            self._state = {}
        super().__init__(**kwargs)

    @property
    def url_base(self) -> str:
        subdomain = "analytics.eu." if self.data_region == "EU Residency Server" else ""
        return f"https://{subdomain}amplitude.com/api/"

    @property
    def time_interval(self) -> dict:
        return {self.event_time_interval.get("size_unit"): self.event_time_interval.get("size")}

    @property
    def state(self) -> Mapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: Mapping[str, Any]) -> Mapping[str, Any]:
        self._state = value

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
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

    def get_most_recent_cursor(self, stream_state: Mapping[str, Any] = None) -> datetime.datetime:
        """
        Use `start_time` instead of `cursor` in the case of more recent.
        This can happen whenever a user simply finds that they are syncing to much data and would like to change `start_time` to be more recent.
        See: https://github.com/airbytehq/airbyte/issues/25367 for more details
        """
        cursor_date = (
            pendulum.parse(stream_state[self.cursor_field])
            if stream_state and self.cursor_field in stream_state
            else datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        )
        return max(self._start_date, cursor_date)

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        most_recent_cursor = self.get_most_recent_cursor(stream_state).strftime(self.compare_date_template)
        try:
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        except zipfile.BadZipFile as e:
            self.logger.exception(e)
            self.logger.error(
                f"Received an invalid zip file in response to URL: {response.request.url}. "
                f"The size of the response body is: {len(response.content)}"
            )
            return []

        for gzip_filename in zip_file.namelist():
            with zip_file.open(gzip_filename) as file:
                for record in self._parse_zip_file(file):
                    if record[self.cursor_field] >= most_recent_cursor:
                        yield self._date_time_to_rfc3339(record)  # transform all `date-time` to RFC3339

    def _parse_zip_file(self, zip_file: IO[bytes]) -> Iterable[MutableMapping]:
        with gzip.open(zip_file) as file:
            for record in file:
                yield json.loads(record)

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        slices = []
        start = self.get_most_recent_cursor(stream_state=stream_state)
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
        try:
            self.logger.info(f"Fetching {self.name} time range: {start.strftime('%Y-%m-%dT%H')} - {end.strftime('%Y-%m-%dT%H')}")
            for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
                self.state = self._get_updated_state(self.state, record)
                yield record
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Error during syncing {self.name} stream - {e}")

    def request_params(self, stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = self.base_params
        params["start"] = pendulum.parse(stream_slice["start"]).strftime(self.date_template)
        params["end"] = pendulum.parse(stream_slice["end"]).strftime(self.date_template)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, **kwargs) -> str:
        return f"{self.api_version}/export"

    def get_error_handler(self) -> ErrorHandler:
        # Error status code mapping from Amplitude documentation: https://amplitude.com/docs/apis/analytics/export#status-codes
        error_mapping = DEFAULT_ERROR_MAPPING | {
            400: ErrorResolution(
                response_action=ResponseAction.FAIL,
                failure_type=FailureType.config_error,
                error_message="The file size of the exported data is too large. Shorten the time ranges and try again. The limit size is 4GB. Provide a shorter 'request_time_range' interval.",
            ),
            403: ErrorResolution(
                response_action=ResponseAction.FAIL,
                failure_type=FailureType.config_error,
                error_message="Access denied due to lack of permission or invalid API/Secret key or wrong data region.",
            ),
            404: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message="No data available for the time range requested.",
            ),
            504: ErrorResolution(
                response_action=ResponseAction.FAIL,
                failure_type=FailureType.config_error,
                error_message="The amount of data is large and may be causing a timeout. For large amounts of data, the Amazon S3 destination is recommended. Refer to Amplitude documentation for information on setting up the S3 destination: https://amplitude.com/docs/data/destination-catalog/amazon-s3#run-a-manual-export",
            ),
        }
        return HttpStatusErrorHandler(logger=LOGGER, error_mapping=error_mapping)
