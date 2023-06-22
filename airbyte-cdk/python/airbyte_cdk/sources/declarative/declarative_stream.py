#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import AirbyteMessage, SyncMode
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.declarative.schema import DefaultSchemaLoader
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice
from airbyte_cdk.sources.streams.core import Stream, StreamData


@dataclass
class DeclarativeStream(Stream):
    """
    DeclarativeStream is a Stream that delegates most of its logic to its schema_load and retriever

    Attributes:
        name (str): stream name
        primary_key (Optional[Union[str, List[str], List[List[str]]]]): the primary key of the stream
        schema_loader (SchemaLoader): The schema loader
        retriever (Retriever): The retriever
        config (Config): The user-provided configuration as specified by the source's spec
        stream_cursor_field (Optional[Union[InterpolatedString, str]]): The cursor field
        transformations (List[RecordTransformation]): A list of transformations to be applied to each output record in the
        stream. Transformations are applied in the order in which they are defined.
    """

    retriever: Retriever
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    name: str
    primary_key: Optional[Union[str, List[str], List[List[str]]]]
    schema_loader: Optional[SchemaLoader] = None
    _name: str = field(init=False, repr=False, default="")
    _primary_key: str = field(init=False, repr=False, default="")
    _schema_loader: SchemaLoader = field(init=False, repr=False, default=None)
    stream_cursor_field: Optional[Union[InterpolatedString, str]] = None
    transformations: List[RecordTransformation] = None

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.stream_cursor_field = InterpolatedString.create(self.stream_cursor_field, parameters=parameters)
        self.transformations = self.transformations or []
        self._schema_loader = self.schema_loader if self.schema_loader else DefaultSchemaLoader(config=self.config, parameters=parameters)

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @primary_key.setter
    def primary_key(self, value: str) -> None:
        if not isinstance(value, property):
            self._primary_key = value

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, property):
            self._name = value

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self.retriever.state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter, accept state serialized by state getter."""
        self.retriever.state = value

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        return self.state

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        cursor = self.stream_cursor_field.eval(self.config)
        return cursor if cursor else []

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        :param: stream_state We knowingly avoid using stream_state as we want cursors to manage their own state.
        """
        for record in self.retriever.read_records(sync_mode, cursor_field, stream_slice):
            yield self._apply_transformations(record, self.config, stream_slice)

    def _apply_transformations(
        self,
        message_or_record_data: StreamData,
        config: Config,
        stream_slice: StreamSlice,
    ):
        # If the input is an AirbyteMessage with a record, transform the record's data
        # If the input is another type of AirbyteMessage, return it as is
        # If the input is a dict, transform it
        if isinstance(message_or_record_data, AirbyteMessage):
            if message_or_record_data.record:
                record = message_or_record_data.record.data
            else:
                return message_or_record_data
        elif isinstance(message_or_record_data, dict):
            record = message_or_record_data
        elif isinstance(message_or_record_data, Record):
            record = message_or_record_data.data
        else:
            # Raise an error because this is unexpected and indicative of a typing problem in the CDK
            raise ValueError(
                f"Unexpected record type. Expected {StreamData}. Got {type(message_or_record_data)}. This is probably due to a bug in the CDK."
            )
        for transformation in self.transformations:
            transformation.transform(record, config=config, stream_state=self.state, stream_slice=stream_slice)

        return message_or_record_data

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
        :param stream_state: we knowingly avoid using stream_state as we want cursors to manage their own state
        :return:
        """
        return self.retriever.stream_slices()

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        """
        We explicitly disable checkpointing here. There are a couple reasons for that and not all are documented here but:
        * In the case where records are not ordered, the granularity of what is ordered is the slice. Therefore, we will only update the
            cursor value once at the end of every slice.
        * Updating the state once every record would generate issues for data feed stop conditions or semi-incremental syncs where the
            important state is the one at the beginning of the slice
        """
        return None
