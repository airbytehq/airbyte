# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import StreamData


@dataclass
class ZendeskSupportAuditLogsIncrementalSync(DatetimeBasedCursor):
    """
    This class is created for the Audit Logs stream. List with time range is used for record filtering.
    """

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        option_type = RequestOptionType.request_parameter
        options: MutableMapping[str, Any] = {}
        if not stream_slice:
            return options

        # set list with time range
        if self.start_time_option and self.start_time_option.inject_into == option_type:
            start_time = stream_slice.get(self._partition_field_start.eval(self.config))
            options[self.start_time_option.field_name.eval(config=self.config)] = [start_time]  # type: ignore # field_name is always casted to an interpolated string
        if self.end_time_option and self.end_time_option.inject_into == option_type:
            options[self.end_time_option.field_name.eval(config=self.config)].append(stream_slice.get(self._partition_field_end.eval(self.config)))  # type: ignore # field_name is always casted to an interpolated string
        return options


class ZendeskSupportExtractorEvents(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            records = response.json().get("ticket_events") or []
        except requests.exceptions.JSONDecodeError:
            records = []

        events = []
        for record in records:
            for event in record.get("child_events", []):
                if event.get("event_type") == "Comment":
                    for prop in ["via_reference_id", "ticket_id", "timestamp"]:
                        event[prop] = record.get(prop)

                    # https://github.com/airbytehq/oncall/issues/1001
                    if not isinstance(event.get("via"), dict):
                        event["via"] = None
                    events.append(event)
        return events


class ZendeskSupportAttributeDefinitionsExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            records = []
            for definition in response.json()["definitions"]["conditions_all"]:
                definition["condition"] = "all"
                records.append(definition)
            for definition in response.json()["definitions"]["conditions_any"]:
                definition["condition"] = "any"
                records.append(definition)
        except requests.exceptions.JSONDecodeError:
            records = []
        return records


class TicketAuditsRetriever(SimpleRetriever):
    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters)

        self.record_selector.transformations = []
        self._start_date = self.config["start_date"]
        self.response_list_name = self._parameters["data_path"]
        self._cursor_field = self._parameters["cursor_field"]
        self._start_date = self.config["start_date"]

        self.cursor = DatetimeBasedCursor(
            config=self.config,
            parameters=self._parameters,
            cursor_datetime_formats=[
                "%Y-%m-%dT%H:%M:%SZ",
            ],
            datetime_format="%Y-%m-%dT%H:%M:%SZ",
            cursor_field=self._cursor_field,
            start_datetime=self._start_date,
        )
        self.stream_slicer = self.cursor

    def _validate_response(self, response: requests.Response, stream_state: Mapping[str, Any]) -> bool:
        """
        Ticket Audits endpoint doesn't allow filtering by date, but all data sorted by descending.
        This method used to stop making requests once we receive a response with cursor value greater than actual cursor.
        This action decreases sync time as we don't filter extra records in parse response.
        """
        data = response.json().get(self.response_list_name, [{}])
        created_at = data[0].get(self._cursor_field, "")
        cursor_date = (stream_state or {}).get(self._cursor_field) or self._start_date
        return created_at >= cursor_date

    def _read_pages(
        self,
        records_generator_fn: Callable[[Optional[requests.Response]], Iterable[StreamData]],
        stream_state: Mapping[str, Any],
        stream_slice: StreamSlice,
    ) -> Iterable[StreamData]:
        pagination_complete = False
        next_page_token = None
        while not pagination_complete:
            response = self._fetch_next_page(stream_state, stream_slice, next_page_token)
            yield from records_generator_fn(response)

            if not response:
                pagination_complete = True
            elif not self._validate_response(response, stream_state):
                pagination_complete = True
            else:
                next_page_token = self._next_page_token(response)
                if not next_page_token:
                    pagination_complete = True
