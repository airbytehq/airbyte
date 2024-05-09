# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar
from typing import Any, List, Mapping, Optional

import pendulum
import requests
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


class MailChimpRecordFilter(RecordFilter):
    """
    Filter applied on a list of Records.
    """

    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.parameters = parameters

    def filter_records(
        self,
        records: List[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> List[Mapping[str, Any]]:
        current_state = [x for x in stream_state.get("states", []) if x["partition"]["id"] == stream_slice.partition["id"]]
        cursor_value = self.get_filter_date(self.config.get("start_date"), current_state)
        return [record for record in records if record[self.parameters["cursor_field"]] > cursor_value] if cursor_value else records

    def get_filter_date(self, start_date: str, state_value: list) -> str:
        """
        Calculate the filter date to pass in the request parameters by comparing the start_date
        with the value of state obtained from the stream_slice.
        If only one value exists, use it by default. Otherwise, return None.
        If no filter_date is provided, the API will fetch all available records.
        """

        start_date_parsed = pendulum.parse(start_date).to_iso8601_string() if start_date else None
        state_date_parsed = (
            pendulum.parse(state_value[0]["cursor"][self.parameters["cursor_field"]]).to_iso8601_string() if state_value else None
        )

        # Return the max of the two dates if both are present. Otherwise return whichever is present, or None.
        if start_date_parsed or state_date_parsed:
            return max(filter(None, [start_date_parsed, state_date_parsed]), default=None)


class MailChimpRecordExtractorEmailActivity(DpathExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        records = super().extract_records(response=response)
        return [{**record, **activity_item} for record in records for activity_item in record.pop("activity", [])]
