#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional
from datetime import datetime, timedelta

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.stream_slicers import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState, Record
from airbyte_cdk.sources.streams.core import Stream
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class AuthenticatorSquare(DeclarativeAuthenticator, JsonSchemaMixin):
    config: Mapping[str, Any]
    bearer: BearerAuthenticator
    oauth: DeclarativeOauth2Authenticator

    def __new__(cls, bearer, oauth, config, *args, **kwargs):
        if config.get("credentials", "api_key"):
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
        
        # The "start" time would be either coming from the configuration (for intial load or reset) or
        # from the saved state. The "state" would keep on getting updated throughout the sync, but we
        # would ignore that value and rely on paging instead to get around Square's 500 record limit.
        start_time_from_config = self._format_datetime(self.start_datetime.get_datetime(self.config, stream_state={}))
        updated_at_from_state = stream_slice.get("original_stream_state_updated_at")
        start_at = max(updated_at_from_state, start_time_from_config) if updated_at_from_state is not None else start_time_from_config
        end_at = stream_slice.get("end_at")

        json_payload["query"] = {
            "filter": {
                "date_time_filter": {
                    "updated_at": {
                        "start_at": start_at,
                        "end_at": end_at,
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

        # Save the original value here, so it doesn't matter what happened to the stream's state, we would still use the correct
        # start time for each batch of locations.
        original_stream_state_updated_at = stream_state.get("updated_at")

        # Also specify a consistent end time. Using the default (no end time) causes the earlier location slices to lose records, because
        # their "end time" is not the same as the end time of later batches. Also, Square API is dropping some records at the time of sync. It
        # could be the same case as in Stitch. Since we are already doing a de-dup by ID, it's safe to go back 5 minutes and let the de-dup process
        # handle the overlap. While we're at it, zero out the seconds. With this in place though, we cannot run the sync more often than every 5 mins.
        end_at = (datetime.now() + timedelta(minutes=-5)).strftime("%Y-%m-%dT%H:%M:00Z")

        # Loop through each batch of 10 locations, passing in the same start time and end time for each batch.
        for location in separated_locations:
            yield {"location_ids": location, "original_stream_state_updated_at": original_stream_state_updated_at, "end_at": end_at}
