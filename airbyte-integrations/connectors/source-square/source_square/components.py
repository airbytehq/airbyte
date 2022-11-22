#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import logging
from dataclasses import InitVar, dataclass
from typing import Any, ClassVar, Iterable, Mapping, MutableMapping, Optional, Union

import pendulum
from dataclasses_jsonschema import JsonSchemaMixin

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.stream_slicers import StreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream


@dataclass
class AuthenticatorSquare(DeclarativeAuthenticator, JsonSchemaMixin):
    config: Mapping[str, Any]
    bearer: BearerAuthenticator
    oauth: DeclarativeOauth2Authenticator

    def __new__(cls, bearer, oauth, config, *args, **kwargs):
        if config.get('api_key'):
            return bearer
        else:
            return oauth


@dataclass
class SquareSlicer(StreamSlicer):
    options: InitVar[Mapping[str, Any]]
    request_cursor_field: str
    cursor_field: str

    START_DATETIME: ClassVar[str] = "1970-01-01T00:00:00+00:00"
    DATETIME_FORMAT: ClassVar[str] = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __post_init__(self, options: Mapping[str, Any]):
        self._state = {}

    def get_stream_state(self) -> StreamState:
        return self._state

    def get_request_params(
            self,
            *,
            stream_state: Optional[StreamState] = None,
            stream_slice: Optional[StreamSlice] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {}

    def get_request_headers(self, *args, **kwargs) -> Mapping[str, Any]:
        return {}

    def get_request_body_data(self, *args, **kwargs) -> Optional[Union[Mapping, str]]:
        return {}

    def get_request_body_json(
            self,
            *,
            stream_state: Optional[StreamState] = {},
            stream_slice: Optional[StreamSlice] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:

        return {}

    def _max_dt_str(self, *args: str) -> Optional[str]:
        new_state_candidates = list(map(lambda x: pendulum.parse(x) if isinstance(x, str) else x, filter(None, args)))
        if not new_state_candidates:
            return
        max_dt = max(new_state_candidates)
        (dt, micro) = max_dt.strftime(self.DATETIME_FORMAT).split(".")
        return "%s.%03dZ" % (dt, int(micro[:-1:]) / 1000)

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        slice_state = stream_slice.get(self.cursor_field)
        current_state = self._state.get(self.cursor_field)
        last_cursor = last_record and last_record[self.cursor_field]
        max_dt = self._max_dt_str(slice_state, current_state, last_cursor)
        if not max_dt:
            return
        self._state[self.cursor_field] = max_dt

    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState, *args, **kwargs) -> Iterable[StreamSlice]:
        yield {self.request_cursor_field: stream_state.get(self.cursor_field, self.START_DATETIME)}


@dataclass
class SquareSubstreamSlicer(SquareSlicer):
    parent_stream: Stream
    locations_per_request = 10

    @property
    def logger(self):
        return logging.getLogger(f"airbyte.streams.{self.parent_stream.name}")

    def get_request_body_json(
            self,
            *,
            stream_state: Optional[StreamState] = {},
            stream_slice: Optional[StreamSlice] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        json_payload = {"cursor": next_page_token["cursor"]} if next_page_token else {}
        if stream_slice:
            json_payload.update(stream_slice)
        json_payload["query"] = {
            "filter": {
                "date_time_filter": {
                    "updated_at": {
                        "start_at": stream_state.get(self.cursor_field, self.START_DATETIME),
                    }
                }
            },
            "sort": {
                "sort_field": "UPDATED_AT",
                "sort_order": "ASC"
            }
        }
        return json_payload

    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState, *args, **kwargs) -> Iterable[StreamSlice]:
        locations_records = self.parent_stream.read_records(sync_mode=SyncMode.full_refresh)
        location_ids = [location["id"] for location in locations_records]

        if not location_ids:
            self.logger.error(
                "No locations found. Orders cannot be extracted without locations. "
                "Check https://developer.squareup.com/explorer/square/locations-api/list-locations"
            )
            yield from []
        separated_locations = [location_ids[i:i + self.locations_per_request] for i in
                               range(0, len(location_ids), self.locations_per_request)]
        for location in separated_locations:
            yield {"location_ids": location}
