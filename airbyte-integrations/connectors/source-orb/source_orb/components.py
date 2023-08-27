#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests

from dataclasses import dataclass
from typing import Optional

from airbyte_cdk.sources.declarative.transformations.transformation import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


@dataclass
class EventPropertiesTransformation(RecordTransformation):

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:

        # Nothing to extract for each ledger entry
        merged_properties_keys = (config.string_event_properties_keys or []) + (config.numeric_event_properties_keys or [])
        if not merged_properties_keys:
            return record

        # The events endpoint is a `POST` endpoint which expects a list of event_ids to filter on
        event_id = record.id
        request_filter_json = {"event_ids": [event_id]}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {config.api_key}'
        }

        args = {
            "method": "POST", 
            "url": "https://api.billwithorb.com/v1/events", 
            "json": request_filter_json,
            "headers": headers
        }

        events_response = requests.request(**args)
        events_response.raise_for_status() # Error for invalid responses
        events_response_body = events_response.json()

        for event in events_response_body["data"]:
            if event_id == event["id"]:
                desired_properties_subset = {
                    key: value 
                    for key, value in event["properties"].items() 
                    if key in merged_properties_keys
                }
                
                # Replace ledger_entry.event_id with ledger_entry.event
                record["event"]["properties"] = desired_properties_subset

        return record
