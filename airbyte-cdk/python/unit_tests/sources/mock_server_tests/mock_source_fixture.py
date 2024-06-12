#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource, Source
from airbyte_cdk.sources.streams import CheckpointMixin, IncrementalMixin, Stream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_protocol.models import ConnectorSpecification, SyncMode
from requests import HTTPError


class FixtureAvailabilityStrategy(HttpAvailabilityStrategy):
    """
    Inherit from HttpAvailabilityStrategy with slight modification to 403 error message.
    """

    def reasons_for_unavailable_status_codes(self, stream: Stream, logger: logging.Logger, source: Source, error: HTTPError) -> Dict[int, str]:
        reasons_for_codes: Dict[int, str] = {
            requests.codes.FORBIDDEN: "This is likely due to insufficient permissions for your Notion integration. "
                                      "Please make sure your integration has read access for the resources you are trying to sync"
        }
        return reasons_for_codes


class IntegrationStream(HttpStream, ABC):

    url_base = "https://api.airbyte-test.com/v1/"
    primary_key = "id"
    page_size = 100
    raise_on_http_errors = True
    current_page = 0

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.start_date = config.get("start_date")

    @property
    def availability_strategy(self) -> HttpAvailabilityStrategy:
        return FixtureAvailabilityStrategy()

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("data", [])
        yield from data

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        has_more = response.json().get("has_more")
        if has_more:
            self.current_page += 1
            return {"page": self.current_page}
        else:
            return None


class IncrementalIntegrationStream(IntegrationStream, IncrementalMixin, ABC):
    cursor_field = "created_at"
    _state = {}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        self._state = value

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            self.state = {self.cursor_field: record.get(self.cursor_field)}
            yield record


class Users(IntegrationStream):
    def path(self, **kwargs) -> str:
        return "users"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "type": {
                    "type": "string"
                },
                "id": {
                    "type": "string"
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time"
                },
                "first_name": {
                    "type": "string"
                },
                "last_name": {
                    "type": "string"
                }
            }
        }


class Planets(IncrementalIntegrationStream):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._state: MutableMapping[str, Any] = {}

    def path(self, **kwargs) -> str:
        return "planets"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "type": {
                    "type": "string"
                },
                "id": {
                    "type": "string"
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time"
                },
                "name": {
                    "type": "string"
                }
            }
        }

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {
            "start_date": stream_slice.get("start_date"),
            "end_date": stream_slice.get("end_date")
        }

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = pendulum.parse(self.start_date)

        if stream_state:
            start_date = pendulum.parse(stream_state.get(self.cursor_field))

        date_slices = []

        end_date = datetime.now(timezone.utc).replace(microsecond=0)
        while start_date < end_date:
            end_date_slice = min(start_date.add(days=7), end_date)

            date_slice = {"start_date": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"), "end_date": end_date_slice.strftime("%Y-%m-%dT%H:%M:%SZ")}

            date_slices.append(date_slice)
            start_date = end_date_slice

        return date_slices


class Legacies(IntegrationStream):
    """
    Incremental stream that uses the legacy method get_updated_state() to manage stream state. New connectors use the state
    property and setter methods.
    """

    cursor_field = "created_at"

    def path(self, **kwargs) -> str:
        return "legacies"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "type": {
                    "type": "string"
                },
                "id": {
                    "type": "string"
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time"
                },
                "quote": {
                    "type": "string"
                }
            }
        }

    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> MutableMapping[str, Any]:
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        if current_state:
            return {self.cursor_field: max(latest_state, current_state)}
        return {}

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: Optional[List[str]] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {
            "start_date": stream_slice.get("start_date"),
            "end_date": stream_slice.get("end_date")
        }

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = pendulum.parse(self.start_date)

        if stream_state:
            start_date = pendulum.parse(stream_state.get(self.cursor_field))

        date_slices = []

        end_date = datetime.now(timezone.utc).replace(microsecond=0)
        while start_date < end_date:
            end_date_slice = min(start_date.add(days=7), end_date)

            date_slice = {"start_date": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"), "end_date": end_date_slice.strftime("%Y-%m-%dT%H:%M:%SZ")}

            date_slices.append(date_slice)
            start_date = end_date_slice

        return date_slices


class Dividers(IntegrationStream):
    def path(self, **kwargs) -> str:
        return "dividers"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "type": {
                    "type": "string"
                },
                "id": {
                    "type": "string"
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time"
                },
                "divide_category": {
                    "type": "string"
                }
            }
        }

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        return [{"divide_category": "dukes"}, {"divide_category": "mentats"}]

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {"category": stream_slice.get("divide_category")}


class JusticeSongs(HttpStream, CheckpointMixin, ABC):
    url_base = "https://api.airbyte-test.com/v1/"
    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self._state: MutableMapping[str, Any] = {}

    def path(self, **kwargs) -> str:
        return "justice_songs"

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "type": {
                    "type": "string"
                },
                "id": {
                    "type": "string"
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time"
                },
                "name": {
                    "type": "string"
                },
                "album": {
                    "type": "string"
                }
            }
        }

    @property
    def availability_strategy(self) -> HttpAvailabilityStrategy:
        return FixtureAvailabilityStrategy()

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("data", [])
        yield from data

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        self._state = value

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {
            "page": next_page_token.get("page")
        }

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        yield from self._read_page(cursor_field, stream_slice, stream_state)

    def _read_page(
        self,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        next_page_token = stream_slice
        request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        request_params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        request = self._create_prepared_request(
            path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            headers=request_headers,
            params=request_params,
            json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
        )
        request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        response = self._send_request(request, request_kwargs)
        yield from self.parse_response(response=response)

        self.next_page_token(response)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        current_page = self._state.get("page") or 0
        has_more = response.json().get("has_more")
        if has_more:
            self._state = {"page": current_page + 1}
        else:
            self._state = None


class SourceFixture(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            Dividers(config=config),
            JusticeSongs(config=config),
            Legacies(config=config),
            Planets(config=config),
            Users(config=config),
        ]

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        return ConnectorSpecification(
            connectionSpecification={
                "properties": {
                    "start_date": {
                        "title": "Start Date",
                        "description": "UTC date and time in the format YYYY-MM-DDTHH:MM:SS.000Z. During incremental sync, any data generated before this date will not be replicated. If left blank, the start date will be set to 2 years before the present date.",
                        "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
                        "pattern_descriptor": "YYYY-MM-DDTHH:MM:SS.000Z",
                        "examples": ["2020-11-16T00:00:00.000Z"],
                        "type": "string",
                        "format": "date-time"
                    }
                }
            }
        )
