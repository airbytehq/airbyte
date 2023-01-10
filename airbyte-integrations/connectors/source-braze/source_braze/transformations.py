#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Optional

import dpath
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
            dpath.util.new(_record, parsed_field.path, value)
        return _record
