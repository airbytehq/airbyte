#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import time
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class OnesignalStream(HttpStream, ABC):
    url_base = "https://onesignal.com/api/v1/"

    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.applications = config.get("applications")

        # OneSignal uses epoch timestamp, so we need to convert the start_date
        # config to epoch timestamp too.
        # start_date example: 2021-01-01T00:00:00Z
        self.start_date = pendulum.parse(config["start_date"]).int_timestamp

    def next_page_token(
        self,
        response: requests.Response,
    ) -> Optional[Mapping[str, Any]]:
        return None

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        OneSignal's API rates limit is 1 request per second with a 10/second burst.
        RateLimit* headers will indicate how much quota is left at the time of
        the request. For example:

            ratelimit-limit: 10
            ratelimit-remaining: 9
            ratelimit-reset: 1633654403

        Docs: https://documentation.onesignal.com/docs/rate-limits
        """
        reset_time = response.headers.get("ratelimit-reset")
        backoff_time = float(reset_time) - time.time() if reset_time else 60
        if backoff_time < 0:
            backoff_time = 60
        return backoff_time

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        yield from data

    def check_availability(self, logger: logging.Logger, source: Optional["Source"] = None) -> Tuple[bool, Optional[str]]:
        return True, None


class AppSlicesStream(OnesignalStream):
    def stream_slices(
        self,
        sync_mode: SyncMode,
        **kwargs,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from self.applications

    # default record filter, do nothing
    def filter_by_state(self, **kwargs) -> bool:
        return True

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any], **kwargs
    ) -> Iterable[Mapping]:
        data = response.json().get(self.data_field)
        for record in data:
            if self.filter_by_state(stream_state=stream_state, record=record, stream_slice=stream_slice):
                yield record

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        token = stream_slice.get("app_api_key")
        self._session.auth = TokenAuthenticator(token, "Basic")

        return super().read_records(sync_mode, cursor_field, stream_slice, stream_state)


class IncrementalOnesignalStream(AppSlicesStream, IncrementalMixin, ABC):
    _state = {}
    cursor_field = "updated_at"

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
        """
        An example of response is:
        {
            "total_count": 553,
            "offset": 0,
            "limit": 1,
            "notifications": [ ... ]
        }
        """
        resp = response.json()
        total = resp["total_count"]
        next_offset = resp["offset"] + resp["limit"]
        if next_offset < total:
            return {"offset": next_offset}

    def filter_by_state(
        self, stream_state: Mapping[str, Any] = None, record: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None
    ) -> bool:
        app_id = stream_slice.get("app_id")
        record_value = record.get(self.cursor_field, 0)
        cursor_value = max(stream_state.get(app_id, {}).get(self.cursor_field, 0), record_value)
        self.state = {app_id: {self.cursor_field: cursor_value}}
        return not stream_state or stream_state.get(app_id, {}).get(self.cursor_field, 0) < record_value

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state.update(value)


class Apps(OnesignalStream):
    """
    Docs: https://documentation.onesignal.com/reference/view-apps-apps
    """

    def path(self, **kwargs) -> str:
        return self.name


class Devices(IncrementalOnesignalStream):
    """
    Docs: https://documentation.onesignal.com/reference/view-devices
    """

    cursor_field = "last_active"
    data_field = "players"
    page_size = 300  # page size limit set by OneSignal

    def path(self, **kwargs) -> str:
        return "players"


class Notifications(IncrementalOnesignalStream):
    """
    Docs: https://documentation.onesignal.com/reference/view-notifications
    """

    cursor_field = "queued_at"
    data_field = "notifications"
    page_size = 50  # page size limit set by OneSignal

    def path(self, **kwargs) -> str:
        return self.name


class Outcomes(AppSlicesStream):
    """
    Docs: https://documentation.onesignal.com/reference/view-outcomes
    """

    data_field = "outcomes"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outcome_names = kwargs["config"]["outcome_names"]

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
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
