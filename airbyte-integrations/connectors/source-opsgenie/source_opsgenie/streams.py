#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time
import urllib.parse as urlparse
from abc import ABC
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import parse_qs

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class OpsgenieStream(HttpStream, ABC):

    primary_key = "id"
    api_version = "v2"

    flatten_id_keys = []
    flatten_list_keys = []

    def __init__(self, endpoint: str, **kwargs):
        super(OpsgenieStream, self).__init__(**kwargs)
        self._endpoint = endpoint

    @property
    def url_base(self) -> str:
        return f"https://{self._endpoint}/{self.api_version}/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        params = {}
        data = response.json()
        if "paging" in data and "next" in data["paging"]:
            next_page = data["paging"]["next"]
            params = parse_qs(urlparse.urlparse(next_page).query)

        return params

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params: Dict[str, str] = {}

        if next_page_token:
            params.update(next_page_token)

        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json()
        data = response_data["data"]
        if isinstance(data, list):
            for record in data:
                yield self.transform(record, **kwargs)
        elif isinstance(data, dict):
            yield self.transform(data, **kwargs)
        else:
            Exception(f"Unsupported type of response data for stream {self.name}")

    def transform(self, record: Dict[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs):
        for key in self.flatten_id_keys:
            self._flatten_id(record, key)

        for key in self.flatten_list_keys:
            self._flatten_list(record, key)

        return record

    def _flatten_id(self, record: Dict[str, Any], target: str):
        target_value = record.pop(target, None)
        record[target + "_id"] = target_value.get("id") if target_value else None

    def _flatten_list(self, record: Dict[str, Any], target: str):
        record[target] = [target_data.get("id") for target_data in record.get(target, [])]

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        This method is called if we run into the rate limit.
        Opsgenie applies rate limits in both requests-per-minute and
        requests-per-second buckets. The response will inform which
        of these thresholds has been breached by returning a X-RateLimit-Period-In-Sec
        header value of 60 and 1 respectively. We take this as the hint for how long
        to wait before trying again.

        Rate Limits Docs: https://docs.opsgenie.com/docs/api-rate-limiting
        """

        if "X-RateLimit-Period-In-Sec" in response.headers:
            return int(response.headers["X-RateLimit-Period-In-Sec"])
        else:
            self.logger.info("X-RateLimit-Period-In-Sec header not found. Using default backoff value")
            return 60


class Teams(OpsgenieStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "teams"


class Integrations(OpsgenieStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "integrations"


class Users(OpsgenieStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "users"


class Services(OpsgenieStream):

    api_version = "v1"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "services"


class OpsgenieChildStream(OpsgenieStream):
    path_list = ["id"]
    flatten_parent_id = False

    def __init__(self, parent_stream: OpsgenieStream, **kwargs):
        super().__init__(**kwargs)
        self.parent_stream = parent_stream

    @property
    def path_template(self) -> str:
        template = [self.parent_stream.name] + ["{" + path_key + "}" for path_key in self.path_list]
        return "/".join(template + [self.name])

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for slice in self.parent_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            for record in self.parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice):
                yield {path_key: record[path_key] for path_key in self.path_list}

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return self.path_template.format(**{path_key: stream_slice[path_key] for path_key in self.path_list})

    def transform(self, record: Dict[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs):
        record = super().transform(record, stream_slice, **kwargs)
        if self.flatten_parent_id:
            record[f"{self.parent_stream.name[:-1]}_id"] = stream_slice["id"]
        return record


class UserTeams(OpsgenieChildStream):
    flatten_parent_id = True
    path_template = "users/{id}/teams"


# Basic incremental stream
class IncrementalOpsgenieStream(OpsgenieStream, ABC):
    def __init__(self, start_date, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date

    state_checkpoint_interval = 100
    cursor_field = "updatedAt"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        cursor_field = self.cursor_field
        latest_record = latest_record.get(self.cursor_field)

        latest_record_date = pendulum.parse(latest_record)
        stream_state = current_stream_state.get(cursor_field)
        if stream_state:
            return {cursor_field: str(max(latest_record_date, pendulum.parse(stream_state)))}
        else:
            return {cursor_field: str(latest_record_date)}

    def request_params(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        start_point = self.start_date
        start_date_dt = pendulum.parse(start_point)

        state_value = stream_state.get(self.cursor_field)
        if state_value:
            state_value_dt = pendulum.parse(state_value)
            start_date_dt = max(start_date_dt, state_value_dt)
            start_date_dt = min(start_date_dt, pendulum.now())

        dt_timestamp = int(time.mktime(start_date_dt.timetuple()) * 1000)

        params["query"] = [f"{self.cursor_field}>={dt_timestamp}"]
        params["order"] = ["asc"]

        return params


class Alerts(IncrementalOpsgenieStream):
    def path(self, **kwargs) -> str:
        return "alerts"


class Incidents(IncrementalOpsgenieStream):

    api_version = "v1"

    def path(self, **kwargs) -> str:
        return "incidents"


class AlertRecipients(OpsgenieChildStream):
    flatten_parent_id = True
    path_template = "alerts/{id}/recipients"
    flatten_id_keys = ["user"]
    primary_key = "user_id"


class AlertLogs(OpsgenieChildStream):
    primary_key = "offset"
    cursor_field = "offset"
    path_template = "alerts/{id}/logs"
    flatten_parent_id = True

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        alert_id = latest_record.get("alert_id")
        latest_cursor_value = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(str(alert_id))
        if current_state:
            current_state = current_state.get(self.cursor_field)
        current_state_value = current_state or latest_cursor_value
        max_value = max(current_state_value, latest_cursor_value)
        current_stream_state[str(alert_id)] = {self.cursor_field: str(max_value)}
        return current_stream_state

    def request_params(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        stream_state = stream_state or {}
        params = super().request_params(stream_state, stream_slice, next_page_token)

        state_alert_value = stream_state.get(str(stream_slice["id"]))
        if state_alert_value:
            state_value = state_alert_value.get(self.cursor_field)
            if state_value:
                params[self.cursor_field] = [state_value]
        params["order"] = ["asc"]
        return params
