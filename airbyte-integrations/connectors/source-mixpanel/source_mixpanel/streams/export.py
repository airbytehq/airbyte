#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from functools import cache
from typing import Any, Iterable, Mapping, MutableMapping

import pendulum
import requests
from airbyte_cdk.models import SyncMode

from ..property_transformation import transform_property_names
from .base import DateSlicesMixin, IncrementalMixpanelStream, MixpanelStream


class ExportSchema(MixpanelStream):
    """
    Export helper stream for dynamic schema extraction.
    :: reqs_per_hour_limit: int - property is set to the value of 1 million,
       to get the sleep time close to the zero, while generating dynamic schema.
       When `reqs_per_hour_limit = 0` - it means we skip this limits.
    """

    primary_key: str = None
    data_field: str = None
    reqs_per_hour_limit: int = 0  # see the docstring

    def path(self, **kwargs) -> str:
        return "events/properties/top"

    def process_response(self, response: requests.Response, **kwargs) -> Iterable[str]:
        """
        response.json() example:
        {
            "$browser": {
                "count": 6
            },
            "$browser_version": {
                "count": 6
            },
            "$current_url": {
                "count": 6
            },
            "mp_lib": {
                "count": 6
            },
            "noninteraction": {
                "count": 6
            },
            "$event_name": {
                "count": 6
            },
            "$duration_s": {},
            "$event_count": {},
            "$origin_end": {},
            "$origin_start": {}
        }
        """
        records = response.json()
        for property_name in records:
            yield property_name


class Export(DateSlicesMixin, IncrementalMixpanelStream):
    """Export event data as it is received and stored within Mixpanel, complete with all event properties
     (including distinct_id) and the exact timestamp the event was fired.

    API Docs: https://developer.mixpanel.com/reference/export
    Endpoint: https://data.mixpanel.com/api/2.0/export

    Raw Export API Rate Limit (https://help.mixpanel.com/hc/en-us/articles/115004602563-Rate-Limits-for-API-Endpoints):
     A maximum of 100 concurrent queries,
     3 queries per second and 60 queries per hour.
    """

    primary_key: str = None
    cursor_field: str = "time"

    @property
    def url_base(self):
        prefix = "-eu" if self.region == "EU" else ""
        return f"https://data{prefix}.mixpanel.com/api/2.0/"

    def path(self, **kwargs) -> str:
        return "export"

    def iter_dicts(self, lines):
        """
        The incoming stream has to be JSON lines format.
        From time to time for some reason, the one record can be split into multiple lines.
        We try to combine such split parts into one record only if parts go nearby.
        """
        parts = []
        for record_line in lines:
            if record_line == "terminated early":
                self.logger.warning(f"Couldn't fetch data from Export API. Response: {record_line}")
                return
            try:
                yield json.loads(record_line)
            except ValueError:
                parts.append(record_line)
            else:
                parts = []

            if len(parts) > 1:
                try:
                    yield json.loads("".join(parts))
                except ValueError:
                    pass
                else:
                    parts = []

    def process_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """Export API return response in JSONL format but each line is a valid JSON object
        Raw item example:
            {
                "event": "Viewed E-commerce Page",
                "properties": {
                    "time": 1623860880,
                    "distinct_id": "1d694fd9-31a5-4b99-9eef-ae63112063ed",
                    "$browser": "Chrome",                                           -> will be renamed to "browser"
                    "$browser_version": "91.0.4472.101",
                    "$current_url": "https://unblockdata.com/solutions/e-commerce/",
                    "$insert_id": "c5eed127-c747-59c8-a5ed-d766f48e39a4",
                    "$mp_api_endpoint": "api.mixpanel.com",
                    "mp_lib": "Segment: analytics-wordpress",
                    "mp_processing_time_ms": 1623886083321,
                    "noninteraction": true
                }
            }
        """

        # We prefer response.iter_lines() to response.text.split_lines() as the later can missparse text properties embeding linebreaks
        for record in self.iter_dicts(response.iter_lines(decode_unicode=True)):
            # transform record into flat dict structure
            item = {"event": record["event"]}
            properties = record["properties"]
            for result in transform_property_names(properties.keys()):
                # Convert all values to string (this is default property type)
                # because API does not provide properties type information
                item[result.transformed_name] = str(properties[result.source_name])

            # convert timestamp to datetime string
            item["time"] = pendulum.from_timestamp(int(item["time"]), tz="UTC").to_iso8601_string()

            yield item

    @cache
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.

        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.
        """

        schema = super().get_json_schema()

        # Set whether to allow additional properties for engage and export endpoints
        # Event and Engage properties are dynamic and depend on the properties provided on upload,
        #   when the Event or Engage (user/person) was created.
        schema["additionalProperties"] = self.additional_properties

        # read existing Export schema from API
        schema_properties = ExportSchema(**self.get_stream_params()).read_records(sync_mode=SyncMode.full_refresh)
        for result in transform_property_names(schema_properties):
            # Schema does not provide exact property type
            # string ONLY for event properties (no other datatypes)
            # Reference: https://help.mixpanel.com/hc/en-us/articles/360001355266-Event-Properties#field-size-character-limits-for-event-properties
            schema["properties"][result.transformed_name] = {"type": ["null", "string"]}

        return schema

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        mapping = super().request_params(stream_state, stream_slice, next_page_token)
        if stream_state and "date" in stream_state:
            timestamp = int(pendulum.parse(stream_state["date"]).timestamp())
            mapping["where"] = f'properties["$time"]>=datetime({timestamp})'
        return mapping

    def request_kwargs(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"stream": True}
