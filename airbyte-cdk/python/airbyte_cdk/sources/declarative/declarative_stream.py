#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.declarative.schema import DefaultSchemaLoader
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.types import Config, StreamSlice
from airbyte_cdk.sources.streams.core import Stream


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
    stream_cursor_field: Optional[Union[InterpolatedString, str]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._stream_cursor_field = (
            InterpolatedString.create(self.stream_cursor_field, parameters=parameters)
            if isinstance(self.stream_cursor_field, str)
            else self.stream_cursor_field
        )
        self._schema_loader = self.schema_loader if self.schema_loader else DefaultSchemaLoader(config=self.config, parameters=parameters)

    @property  # type: ignore
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @primary_key.setter
    def primary_key(self, value: str) -> None:
        if not isinstance(value, property):
            self._primary_key = value

    @property  # type: ignore
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
        return self.retriever.state  # type: ignore

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        """State setter, accept state serialized by state getter."""
        self.retriever.state = value

    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> MutableMapping[str, Any]:
        return self.state

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        cursor = self._stream_cursor_field.eval(self.config)
        return cursor if cursor else []

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        :param: stream_state We knowingly avoid using stream_state as we want cursors to manage their own state.
        """
        if stream_slice is None:
            # As the parameter is Optional, many would just call `read_records(sync_mode)` during testing without specifying the field
            # As part of the declarative model without custom components, this should never happen as the CDK would wire up a
            # SinglePartitionRouter that would create this StreamSlice properly
            # As part of the declarative model with custom components, a user that would return a `None` slice would now have the default
            # empty slice which seems to make sense.
            stream_slice = StreamSlice(partition={}, cursor_slice={})
        if not isinstance(stream_slice, StreamSlice):
            raise ValueError(f"DeclarativeStream does not support stream_slices that are not StreamSlice. Got {stream_slice}")
        yield from self.retriever.read_records(self.get_json_schema(), stream_slice)

    def get_json_schema(self) -> Mapping[str, Any]:  # type: ignore
        """
        :return: A dict of the JSON schema representing this stream.

        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.
        """
        return self._schema_loader.get_json_schema()

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[StreamSlice]]:
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
