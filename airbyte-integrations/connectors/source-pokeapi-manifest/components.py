#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional

import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig, SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.transformations import AddFields
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


@dataclass
class ListAddFields(AddFields):
    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        kwargs = {"record": record, "stream_state": stream_state, "stream_slice": stream_slice}
        for parsed_field in self._parsed_fields:
            values = parsed_field.value.eval(config, **kwargs)
            # id_list = [value.get("id") for value in values]
            dpath.util.new(record, parsed_field.path, values)

        return record
