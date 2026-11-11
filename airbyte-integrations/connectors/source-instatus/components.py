#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional

import dpath.util

from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig, SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.transformations import AddFields
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


@dataclass
class ListAddFields(AddFields):
    """
    ListAddFields uses to transform record by adding an ids from list object field to one list.

    input:
    {
         ...,
        "updates": [{
        {
        "id": "some id",...
        },
        {
        "id": "some id",...
        },
        ...
        }]
    }

    output:
    {
         ...,
        "updates_ids": ["some id", "some id", ...]
        "updates": [{
        {
        "id": "some id",...
        },
        {
        "id": "some id",...
        },
        ...
        }]
    }
    """

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
            id_list = [value.get("id") for value in values]
            dpath.util.new(record, parsed_field.path, id_list)

        return record


@dataclass
class UpdatesSubstreamPartitionRouter(SubstreamPartitionRouter):
    """
    UpdatesSubstreamPartitionRouter iterates over the list of id to create a correct stream slices.

    In case we need to make request from parent stream with list of object by their ids we need to use
    a ListAddFields transformer class -> put oll object ids in custom list field -> UpdatesSubstreamPartitionRouter puts every
    id from that list to slices.
    """

    parent_stream_configs: List[ParentStreamConfig]
    parameters: InitVar[Mapping[str, Any]]

    def stream_slices(self) -> Iterable[StreamSlice]:
        if not self.parent_stream_configs:
            yield from []
        else:
            for parent_stream_config in self.parent_stream_configs:
                parent_stream = parent_stream_config.stream
                parent_field = parent_stream_config.parent_key.eval(self.config)
                partition_field = parent_stream_config.partition_field.eval(self.config)

                for parent_partition in parent_stream.generate_partitions():
                    parent_slice = parent_partition.to_slice()

                    for parent_record in parent_partition.read():
                        record_data = parent_record.data
                        stream_state_values = record_data.get(parent_field)
                        updates_object_id = record_data.get("id")

                        for stream_state_value in stream_state_values:
                            yield StreamSlice(
                                partition={partition_field: stream_state_value, "parent_slice": parent_slice},
                                cursor_slice={"updates_object_id": updates_object_id},
                            )
