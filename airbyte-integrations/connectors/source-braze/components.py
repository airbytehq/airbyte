#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import operator
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import dpath
import requests

from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.transformations import AddFields
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState


@dataclass
class TransformToRecordComponent(AddFields):
    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        """
        Transforms incoming string to a dictionary record.
        """
        _record = {}
        kwargs = {"record": record, "stream_state": stream_state, "stream_slice": stream_slice}
        for parsed_field in self._parsed_fields:
            value = parsed_field.value.eval(config, **kwargs)
            dpath.new(_record, parsed_field.path, value)
        return _record


@dataclass
class DatetimeIncrementalSyncComponent(DatetimeBasedCursor):
    """
    Extends DatetimeBasedCursor by adding a required length parameter for the Braze API.
    """
    step_option: Optional[RequestOption] = field(default=None)

    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters=parameters)
        if self.step_option is None:
            raise ValueError("step_option is required for DatetimeIncrementalSyncComponent")

    def _get_request_options(
        self, option_type: RequestOptionType, stream_slice: Optional[StreamSlice] = None
    ) -> Mapping[str, Any]:
        options: dict[str, Any] = {}
        if stream_slice is not None and self.step_option is not None:
            base_options = super()._get_request_options(option_type, stream_slice)
            options.update(base_options)
            
            if self.step_option.inject_into == option_type:
                # Get start and end times from the stream slice
                start_field = self._partition_field_start.eval(self.config)
                end_field = self._partition_field_end.eval(self.config)
                
                start_str = stream_slice.get(start_field)
                end_str = stream_slice.get(end_field)
                
                if isinstance(start_str, str) and isinstance(end_str, str):
                    start_time = self._parser.parse(start_str, self.datetime_format)
                    end_time = self._parser.parse(end_str, self.datetime_format)
                    
                    # Calculate length in days for Braze API (between 1-100)
                    length_days = min(100, max(1, (end_time - start_time).days))
                    
                    field_name = (
                        self.step_option.field_name.eval(config=self.config)
                        if isinstance(self.step_option.field_name, InterpolatedString)
                        else self.step_option.field_name
                    )
                    
                    options[field_name] = length_days

        return options


@dataclass
class EventsRecordExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        response_body = next(self.decoder.decode(response))
        events = response_body.get("events")
        if events:
            return [{"event_name": value} for value in events]
        else:
            return []
