#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.stream_slicers import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class AuthenticatorSquare(DeclarativeAuthenticator, JsonSchemaMixin):
    config: Mapping[str, Any]
    bearer: BearerAuthenticator
    oauth: DeclarativeOauth2Authenticator

    def __new__(cls, bearer, oauth, config, *args, **kwargs):
        if config.get("api_key"):
            return bearer
        else:
            return oauth


@dataclass
class SquareSubstreamSlicer(DatetimeStreamSlicer):
    parent_stream: Stream = None
    parent_key: str = None
    parent_records_per_request: int = 10

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
        initial_start_time = self._format_datetime(self.start_datetime.get_datetime(self.config, stream_state={}))
        json_payload["query"] = {
            "filter": {
                "date_time_filter": {
                    "updated_at": {
                        "start_at": stream_state.get(self.cursor_field.eval(self.config), initial_start_time),
                    }
                }
            },
            "sort": {"sort_field": "UPDATED_AT", "sort_order": "ASC"},
        }
        return json_payload

    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState, *args, **kwargs) -> Iterable[StreamSlice]:
        locations_records = self.parent_stream.read_records(sync_mode=SyncMode.full_refresh)
        location_ids = [location[self.parent_key] for location in locations_records]

        if not location_ids:
            self.logger.error(
                "No locations found. Orders cannot be extracted without locations. "
                "Check https://developer.squareup.com/explorer/square/locations-api/list-locations"
            )
            yield from []
        separated_locations = [
            location_ids[i : i + self.parent_records_per_request] for i in range(0, len(location_ids), self.parent_records_per_request)
        ]
        for location in separated_locations:
            yield {"location_ids": location}
