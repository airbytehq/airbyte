#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import dpath.util

from airbyte_cdk.sources.declarative.transformations.add_fields import AddFields
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.utils.airbyte_datetime_helpers import AirbyteDateTime


@dataclass
class DateTimeTransformer(AddFields):
    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        kwargs = {"record": record, "stream_state": stream_state, "stream_slice": stream_slice}
        for parsed_field in self._parsed_fields:
            date_time = parsed_field.value.eval(config, **kwargs)
            new_date_time = AirbyteDateTime.from_datetime(
                # Expect non-standard date format, e.g. 'Fri, 01 Jan 2021 00:00:00 +0000'
                datetime.strptime(date_time, "%a, %d %b %Y %H:%M:%S %z"),
            )
            dpath.util.new(record, parsed_field.path, new_date_time)
        return record
