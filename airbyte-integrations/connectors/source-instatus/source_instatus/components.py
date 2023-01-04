#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional

import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.stream_slicers.substream_slicer import ParentStreamConfig, SubstreamSlicer
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
class UpdatesSubstreamSlicer(SubstreamSlicer):
    """
    UpdatesSubstreamSlicer iterates over the list of id to create a correct stream slices.

    In case we need to make request from parent stream with list of object by their ids we need to use
    a ListAddFields transformer class -> put oll object ids in custom list field -> UpdatesSubstreamSlicer puts every
    id from that list to slices.
    """

    parent_stream_configs: List[ParentStreamConfig]
    options: InitVar[Mapping[str, Any]]

    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState) -> Iterable[StreamSlice]:
        if not self.parent_stream_configs:
            yield from []
        else:
            for parent_stream_config in self.parent_stream_configs:
                parent_stream = parent_stream_config.stream
                parent_field = parent_stream_config.parent_key
                stream_state_field = parent_stream_config.stream_slice_field

                for parent_stream_slice in parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=None, stream_state=stream_state):
                    empty_parent_slice = True
                    parent_slice = parent_stream_slice

                    for parent_record in parent_stream.read_records(
                        sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
                    ):
                        # Skip non-records (eg AirbyteLogMessage)
                        if isinstance(parent_record, AirbyteMessage):
                            if parent_record.type == Type.RECORD:
                                parent_record = parent_record.record.data
                            else:
                                continue
                        empty_parent_slice = False
                        stream_state_values = parent_record.get(parent_field)
                        updates_object_id = parent_record.get("id")

                        for stream_state_value in stream_state_values:
                            yield {
                                stream_state_field: stream_state_value,
                                "updates_object_id": updates_object_id,
                                "parent_slice": parent_slice,
                            }

                    # If the parent slice contains no records,
                    if empty_parent_slice:
                        yield from []
