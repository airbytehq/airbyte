import time
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from datetime import datetime

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class OnesignalStream(HttpStream, ABC):

    url_base = "https://onesignal.com/api/v1/"

    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self._auth_token = config["user_auth_key"]
        self.start_date = 0
        if isinstance(config.get("start_date"), str):
            # OneSignal uses epoch timestamp, so we need to convert the start_date
            # config to epoch timestamp too
            # start_date example: 2021-01-01T00:00:00Z
            self.start_date = int(datetime.fromisoformat(
                config["start_date"].replace('Z','+00:00')
            ).timestamp())

    def next_page_token(
        self,
        response: requests.Response,
    ) -> Optional[Mapping[str, Any]]:
        return None

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        # OneSignal needs different auth token for each app, so we inject it
        # right before read records request.
        # Note: The _session.auth can be replaced when HttpStream provided
        # some ways to get its request authenticator in the future
        token = self._auth_token
        if stream_slice:
            token = stream_slice.get("rest_api_key", token)
        self._session.auth = TokenAuthenticator(token, "Basic")

        return super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        data = response.json()
        yield from data

        # wait a while to avoid rate limit
        time.sleep(1)


class ChildStreamMixin(HttpSubStream):
    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parents = super().stream_slices(sync_mode, cursor_field, stream_state)
        for item in parents:
            parent = item["parent"]
            yield {
                "app_id": parent["id"],
                "rest_api_key": parent["basic_auth_key"],
            }
        yield from []

    # default record filter, do nothing
    def filter_by_state(
        self,
        stream_state: Mapping[str, Any] = None,
        record: Mapping[str, Any] = None
    ) -> Iterable:
        yield record

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        data = response.json().get(self.data_field)
        for record in data:
            yield from self.filter_by_state(stream_state=stream_state, record=record)


class IncrementalOnesignalStream(ChildStreamMixin, OnesignalStream, ABC):

    cursor_field = "updated_at"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # largest time in cursor field across all stream slices
        self.max_cursor_time = self.start_date

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["app_id"] = stream_slice["app_id"]
        params["limit"] = self.page_size
        if next_page_token:
            params["offset"] = next_page_token["offset"]
        return params

    def next_page_token(
        self,
        response: requests.Response,
    ) -> Optional[Mapping[str, Any]]:
        resp = response.json()
        total = resp["total_count"]
        next_offset = resp["offset"] + resp["limit"]
        if next_offset < total:
            return { "offset": next_offset }

    def filter_by_state(
        self,
        stream_state: Mapping[str, Any] = None,
        record: Mapping[str, Any] = None
    ) -> Iterable:
        value = 0
        if record:
            value = record.get(self.cursor_field, value)
        if not stream_state or value >= stream_state.get(self.cursor_field, 0):
            yield record

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        # we don't update state here, just keep a record of maximum cursor field
        # time, state will be updated after syncing the whole stream
        record_date = latest_record.get(self.cursor_field, self.start_date)
        self.max_cursor_time = max(self.max_cursor_time, record_date)
        return current_stream_state


class Apps(OnesignalStream):

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "apps"


class Devices(IncrementalOnesignalStream):

    cursor_field = "created_at"
    data_field = "players"
    page_size = 300      # page size limit set by OneSignal

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "players"


class Notifications(IncrementalOnesignalStream):

    cursor_field = "queued_at"
    data_field = "notifications"
    page_size = 50      # page size limit set by OneSignal

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "notifications"


class Outcomes(ChildStreamMixin, OnesignalStream):

    data_field = "outcomes"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outcome_names = kwargs["config"]["outcome_names"]

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"apps/{stream_slice['app_id']}/outcomes"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["outcome_names"] = self.outcome_names
        return params

