#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class OnesignalStream(HttpStream, ABC):

    url_base = "https://onesignal.com/api/v1/"

    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self._auth_token = config["user_auth_key"]

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

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        yield from data


class ChildStreamMixin(HttpSubStream):

    is_finished = False

    def stream_slices(
        self,
        sync_mode: SyncMode,
        **kwargs,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # get stream slices from parent app's stream slice cache, if it is not
        # set yet, start a full refresh request to get it in full
        app_slices = self.parent._app_slices
        if not app_slices:
            all(super().stream_slices(SyncMode.full_refresh, **kwargs))
            app_slices = self.parent._app_slices
        for app in app_slices:
            # stream sync is finished when it is on the last slice
            self.is_finished = app["app_id"] == app_slices[-1]["app_id"]
            yield app

    # default record filter, do nothing
    def filter_by_state(self, **kwargs) -> bool:
        return True

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        data = response.json().get(self.data_field)
        for record in data:
            if self.filter_by_state(stream_state=stream_state, record=record):
                yield record


class IncrementalOnesignalStream(ChildStreamMixin, OnesignalStream, ABC):

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

    def filter_by_state(self, stream_state: Mapping[str, Any] = None, record: Mapping[str, Any] = None) -> bool:
        value = 0
        if record:
            value = record.get(self.cursor_field, value)
        return not stream_state or value >= int(stream_state.get(self.cursor_field, "0"))

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}
        current_stream_state_date = current_stream_state.get(self.cursor_field, self.start_date)
        latest_record_date = latest_record.get(self.cursor_field, self.start_date)

        return {self.cursor_field: max(current_stream_state_date, latest_record_date)}


class Apps(OnesignalStream):
    """
    Docs: https://documentation.onesignal.com/reference/view-apps-apps
    """

    # stream slices cache for child streams
    _app_slices = []

    def path(self, **kwargs) -> str:
        return self.name

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # parse response and save to stream slice cache
        self._app_slices = []
        for app in super().parse_response(response, **kwargs):
            slice = {"app_id": app["id"], "rest_api_key": app["basic_auth_key"]}
            self._app_slices.append(slice)
            yield app


class Devices(IncrementalOnesignalStream):
    """
    Docs: https://documentation.onesignal.com/reference/view-devices
    """

    cursor_field = "created_at"
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


class Outcomes(ChildStreamMixin, OnesignalStream):
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
