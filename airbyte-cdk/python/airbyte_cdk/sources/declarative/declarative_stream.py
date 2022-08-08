#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, StreamSlice
from airbyte_cdk.sources.streams.core import Stream


class DeclarativeStream(Stream):
    """
    DeclarativeStream is a Stream that delegates most of its logic to its schema_load and retriever
    """

    def __init__(
        self,
        name: str,
        primary_key,
        schema_loader: SchemaLoader,
        retriever: Retriever,
        config: Config,
        cursor_field: Optional[List[str]] = None,
        transformations: List[RecordTransformation] = None,
        checkpoint_interval: Optional[int] = None,
    ):
        """
        :param name: stream name
        :param primary_key: the primary key of the stream
        :param schema_loader: The schema loader
        :param retriever: The retriever
        :param cursor_field: The cursor field
        :param transformations: A list of transformations to be applied to each output record in the stream. Transformations are applied
        in the order in which they are defined.
        """
        self._name = name
        self._config = config
        self._primary_key = primary_key
        self._cursor_field = cursor_field or []
        self._schema_loader = schema_loader
        self._retriever = retriever
        self._transformations = transformations or []
        self._checkpoint_interval = checkpoint_interval

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        return self._name

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        """
        Decides how often to checkpoint state (i.e: emit a STATE message). E.g: if this returns a value of 100, then state is persisted after reading
        100 records, then 200, 300, etc.. A good default value is 1000 although your mileage may vary depending on the underlying data source.

        Checkpointing a stream avoids re-reading records in the case a sync is failed or cancelled.

        return None if state should not be checkpointed e.g: because records returned from the underlying data source are not returned in
        ascending order with respect to the cursor field. This can happen if the source does not support reading records in ascending order of
        created_at date (or whatever the cursor is). In those cases, state must only be saved once the full stream has been read.
        """
        return self._checkpoint_interval

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._retriever.state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter, accept state serialized by state getter."""
        self._retriever.state = value

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        return self.state

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        return self._cursor_field

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in self._retriever.read_records(sync_mode, cursor_field, stream_slice, stream_state):
            yield self._apply_transformations(record, self._config, stream_slice)

    def _apply_transformations(self, record: Mapping[str, Any], config: Config, stream_slice: StreamSlice):
        output_record = record
        for transformation in self._transformations:
            output_record = transformation.transform(record, config=config, stream_state=self.state, stream_slice=stream_slice)

        return output_record

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.

        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.
        """
        return self._schema_loader.get_json_schema()

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override to define the slices for this stream. See the stream slicing section of the docs for more information.

        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return:
        """
        # this is not passing the cursor field because it is known at init time
        return self._retriever.stream_slices(sync_mode=sync_mode, stream_state=stream_state)
