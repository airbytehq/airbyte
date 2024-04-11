# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState

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
