#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import operator
from dataclasses import dataclass
from typing import Any, Mapping, Optional

import dpath
import requests
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.transformations import AddFields
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


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
    Extending DatetimeBasedCursor by adding step option to existing start_time/end_time options
    """

    step_option: Optional[RequestOption] = None
    stream_state_field_step: Optional[str] = None

    def __post_init__(self, parameters: Mapping[str, Any]):
        super(DatetimeIncrementalSyncComponent, self).__post_init__(parameters=parameters)

        self.stream_slice_field_step = InterpolatedString.create(self.stream_state_field_step or "step", parameters=parameters)

    def _get_request_options(self, option_type: RequestOptionType, stream_slice: StreamSlice):
        options = super(DatetimeIncrementalSyncComponent, self)._get_request_options(option_type, stream_slice)
        if self.step_option and self.step_option.inject_into == option_type:
            options[self.step_option.field_name] = stream_slice.get(self.stream_slice_field_step.eval(self.config))
        return options

    def _partition_daterange(self, start, end, step: datetime.timedelta):
        """
        Puts a step to each stream slice. `step` is a difference between start/end date in days.
        """
        get_start_time = operator.itemgetter(self._partition_field_start.eval(self.config))
        get_end_time = operator.itemgetter(self._partition_field_end.eval(self.config))
        date_range = [
            dr
            for dr in super(DatetimeIncrementalSyncComponent, self)._partition_daterange(start, end, step)
            if get_start_time(dr) < get_end_time(dr)
        ]
        for i, _slice in enumerate(date_range):
            start_time = self._parser.parse(get_start_time(_slice), self._start_datetime.datetime_format)
            end_time = self._parser.parse(get_end_time(_slice), self._end_datetime.datetime_format)
            _slice._stream_slice[self.stream_slice_field_step.eval(self.config)] = (end_time + datetime.timedelta(days=int(bool(i))) - start_time).days
        return date_range


@dataclass
class EventsRecordExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> list[Record]:
        response_body = self.decoder.decode(response)
        events = response_body.get("events")
        if events:
            return [{"event_name": value} for value in events]
        else:
            return []
