#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Optional

import dpath.util
import pendulum

from airbyte_cdk.sources.declarative.transformations.add_fields import AddFields
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


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
            new_date_time = str(pendulum.from_format(date_time, "ddd, D MMM YYYY HH:mm:ss ZZ"))
            dpath.util.new(record, parsed_field.path, new_date_time)
        return record
